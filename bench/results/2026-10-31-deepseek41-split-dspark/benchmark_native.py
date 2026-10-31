#!/usr/bin/env python3
"""Replay the synthetic 16K/2K benchmark with Abyss's native stdio protocol.

Run only while the selected GPUs are available. This never stops any service.
Uses only Python's standard library; no tokenizer or network access is needed.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import queue
import signal
import statistics
import subprocess
import threading
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', required=True)
    ap.add_argument('--pack', required=True)
    ap.add_argument('--drafter', help='V4.1 DSpark GGUF, required for *-on modes')
    ap.add_argument('--mode', choices=['single-off', 'single-on', 'split-off', 'split-on'], required=True)
    ap.add_argument('--devices', help='Physical GPU order; default 1 for single, 0,1 for split')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--fixtures', type=Path, default=Path(__file__).with_name('benchmark-fixtures.json.gz'))
    ap.add_argument('--ram-gib', type=float, default=119.20928955078125)
    args = ap.parse_args()
    enabled = args.mode.endswith('-on')
    split = args.mode.startswith('split-')
    if enabled and not args.drafter:
        ap.error('--drafter is required for DSpark ON')
    engine = str(Path(args.engine).resolve(strict=True))
    pack = str(Path(args.pack).resolve(strict=True))
    drafter = str(Path(args.drafter).resolve(strict=True)) if enabled else None
    args.out.mkdir(parents=True, exist_ok=False)
    fixtures = json.loads(gzip.decompress(args.fixtures.read_bytes()))
    for fixture in fixtures:
        digest = hashlib.sha256(','.join(map(str, fixture['ids'])).encode()).hexdigest()
        assert digest == fixture['sha256'], fixture['name']
        assert len(fixture['ids']) == 16384 and fixture['cap'] == 2048

    env = {k: v for k, v in os.environ.items() if not k.startswith(('STRATA_', 'DS4_', 'MAYA_'))}
    env.update({
        'CUDA_DEVICE_ORDER': 'PCI_BUS_ID',
        'CUDA_VISIBLE_DEVICES': args.devices or ('0,1' if split else '1'),
        'STRATA_GLM_SPLIT': '8' if split else '0',
        'STRATA_GLM_RAM_GB': str(args.ram_gib),
        'STRATA_GLM_CPU_LANE': '12',
        'STRATA_GLM_NO_SPEC': '1',
        'STRATA_DS4_SPEC': '1' if enabled else '0',
        'STRATA_GLM_NO_REUSE': '1',
        'STRATA_GLM_USAGE': '0',
        'STRATA_GLM_KDA_GRAPH': '0',
        'STRATA_GLM_TAIL_SKIP': '0',
        'STRATA_GLM_TAIL_SKIP_W': '0',
        'STRATA_GLM_TAIL_SKIP_DISK': '0',
        'STRATA_GLM_PREFILL_TAIL_SKIP': '0',
    })
    if enabled:
        env['STRATA_DS4_DSPARK'] = drafter
    command = [engine, '--serve', '--glm-pack', pack, '--max-context', '32768',
               '--prefill', '4096', '--spec', '5' if enabled else '0', '--layer-split', '0']
    (args.out / 'settings.json').write_text(json.dumps({
        'command': command, 'environment': {k: v for k, v in env.items()
                                          if k.startswith(('STRATA_', 'CUDA_'))}}, indent=2))
    events = queue.Queue()
    proc = None
    transcript = []

    def next_event(deadline):
        try:
            now, line = events.get(timeout=max(.01, deadline - time.monotonic()))
        except queue.Empty:
            raise TimeoutError('Engine response deadline exceeded') from None
        if line is None or line.startswith('ERR'):
            raise RuntimeError('Engine stopped: ' + str(line))
        return now, line

    try:
        with (args.out / 'engine.stderr.log').open('w') as err:
            proc = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=err, text=True, bufsize=1, start_new_session=True)

            def read_stdout():
                for line in proc.stdout:
                    transcript.append(line)
                    events.put((time.monotonic(), line.rstrip()))
                events.put((time.monotonic(), None))

            thread = threading.Thread(target=read_stdout, daemon=True)
            thread.start()
            load_deadline = time.monotonic() + 600
            while not next_event(load_deadline)[1].startswith('READY '):
                pass
            rows = []
            for fixture in fixtures:
                started = time.monotonic()
                request = (f"GEN {fixture['cap']} temperature=0 top_p=1 top_k=0 min_p=0 seed=42 "
                           f"spec={int(enabled)} cpu_threads=12 " + ','.join(map(str, fixture['ids'])) + '\n')
                proc.stdin.write(request)
                proc.stdin.flush()
                tokens, first = [], None
                while True:
                    now, line = next_event(started + 1200)
                    if line.startswith('T '):
                        first = now if first is None else first
                        tokens.append(int(line.split()[1]))
                    elif line.startswith('DONE '):
                        fields = line.split()
                        nout, nin = int(fields[1]), int(fields[2])
                        pms, dms = float(fields[3]), float(fields[4])
                        assert nin == 16384 and nout == len(tokens) == 2048
                        assert int(fields[8]) == 0, 'Unexpected prompt reuse'
                        row = {'name': fixture['name'], 'input_tokens': nin, 'output_tokens': nout,
                               'input_ids_sha256': fixture['sha256'], 'output_ids': tokens,
                               'prefill_tps': nin * 1000 / pms, 'decode_tps': nout * 1000 / dms,
                               'ttft_s': first - started, 'wall_s': now - started,
                               'draft_accepted': int(fields[6]), 'draft_offered': int(fields[7]),
                               'reused': int(fields[8]), 'done': line}
                        (args.out / (fixture['name'] + '.json')).write_text(json.dumps(row, indent=2))
                        print(json.dumps({k: v for k, v in row.items() if k != 'output_ids'}), flush=True)
                        if not fixture['name'].startswith('warmup'):
                            if enabled:
                                assert row['draft_offered'] > 0 and row['draft_accepted'] > 0, 'DSpark inactive'
                            else:
                                assert row['draft_offered'] == 0, 'Unexpected speculation'
                            rows.append(row)
                        break
            summary = {'mode': args.mode, 'measured_requests': len(rows),
                       'metrics': {k: {'median': statistics.median(r[k] for r in rows),
                                       'values': [r[k] for r in rows]}
                                   for k in ['prefill_tps', 'decode_tps', 'ttft_s', 'wall_s']}}
            (args.out / 'summary.json').write_text(json.dumps(summary, indent=2))
            print(json.dumps(summary), flush=True)
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.stdin.write('QUIT\n')
                proc.stdin.flush()
                proc.wait(timeout=30)
            except (BrokenPipeError, subprocess.TimeoutExpired):
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
        (args.out / 'engine.stdout.log').write_text(''.join(transcript))


if __name__ == '__main__':
    main()
