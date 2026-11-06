# Issue #35: v1.3.117 deterministic and sampled-window checks on the GeForce pair and single card

Pinned unpatched upstream **v1.3.117 / `8d1cb8adfe42c8f8ceaf7e910ec69467754b7178`**, CUDA Release/sm_120a, CUDA 13.0, NVIDIA driver 595.99.02. Engine SHA256 `b3c8a300c441f7eb56a971de643687716e787bda4f8ca20873b31519b14f2a93`. GGML `3cf03257f219afbe7334045ff7c6a06ac68c627d`; its tracked worktree was clean. The inherited source on this evidence branch is not the source used for this engine: build the pinned upstream commit.

These are **numerical/reproducibility diagnostics**, separate from the earlier default-speed tables. No parameter search, full-precision teacher comparison or new speed claim is made. Deterministic repeatability uses the actual RTX5070Ti16GB (physical0, workingGen5x16) -> RTX5060Ti16GB (physical1, workingGen4x4) split 32. The temperature>0 batched verify sampler is checked separately on the single physical 5070 Ti, as explained below. The machine has i5-14400, 128 GB installed RAM, Samsung 990 PRO 1 TB and Ubuntu 24.04.5 / Linux 7.0.0-42. PRO measurements were not added to this bounded real-pair check.

## Model and fixed inputs

Same original `Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf` + `...-00002-of-00002.gguf` (83,617,662,656 bytes), unmodified native pack and RT MTP assets. No PLE replacement, DSpark, model conversion or weight download. The shipped expert prior is unchanged, SHA256 `d62f4f0da4e8de44e05fdac38e9965855df12d64f6d21df29d05bdfc246ed721`.

All 22 primary requests submit 16,384 original public synthetic input IDs and generate 2,048 IDs. Shared limits are context 32768, chunk 4096, RAM 90 GiB, `NO_REUSE=1`, `USAGE=0`, seed 42, top_p 1 / top_k 0 / min_p 0. The 14 split requests use `CUDA_VISIBLE_DEVICES=0,1`, split 32; the eight active-sampler requests use `CUDA_VISIBLE_DEVICES=0` with no layer split. Next GEN is dispatched immediately after DONE; the final request is followed by QUIT and verified process exit. Exact inputs/output IDs and all native timings are retained, but diagnostic timings are not benchmark results.

Important: deterministic mode **preserves explicitly set switches**. This harness normally sets a CPU lane, so for this check it explicitly sets `STRATA_GLM_CPU_LANE=0` and request `cpu_threads=0`. The mode itself defaults unset prompt CPU/iGPU, decodeiGPU, promotion/fill, read-ahead/RAMfill, prestage adaptation, usage and n-gram gate switches to0. The emitted startup note is retained:

> NOTE: STRATA_DETERMINISTIC: timing-driven choices off (CPU / iGPU lanes, tier moves, the n-gram gate) - slower, for equality tests; kept as set: STRATA_GLM_CPU_LANE=0 STRATA_GLM_USAGE=0

This changes scheduling/residency conditions from the old CPU 8 shared speed runs. Merely adding the flag to a config with CPU 8 does not disable that explicitly configured lane.

## Greedy repeatability

Two fresh native processes, each one full warmup plus two repeated requests, all using exactly the same original trial-01 input (SHA256 `09b21ed21f83c029880a8c820c1fd905f2732103490274dba6fc4fc3f16c51f8`). The aliases `repro-warmup-01`, `repro-repeat-01` and `repro-repeat-02` contain identical IDs, with their own retained records.

The six responses contain **3 distinct output hashes**. Across the two fresh starts, corresponding request ordinals match **3/3** in all 2,048 IDs and **3/3** in draft accepted/offered counts. All six outputs invariant to request ordinal: **False**; draft counts invariant: **False**.

| Request ordinal in each start | First output ID (start1) | Full output hash (start1) | Accepted/offered (start1) | All2048IDs match start2 at same ordinal |
|---:|---:|---|---:|---|
| 0 | 13962 | `8178c21761a7e036b6140d9f8eb3dd1cfa44a9c7769e5429d26dab41ccbdc189` | 1079/1406 | True |
| 1 | 9333 | `a8429675d16520dfbb30cf80d11f4d0c3ad511f847fc4c1da1b2b66fc083f310` | 1082/1408 | True |
| 2 | 9333 | `bbbcc4009145ee141552b22af0ffb32ffd85a5db0feca0994c35d017c82dc64c` | 1169/1495 | True |

The warmup is ordinal0. Per-response output hashes and first-difference comparisons, including every row of start2, are in results.json. This checks reproduction of a whole recorded request sequence across two fresh starts. It does not establish that repeating an identical prompt later in one process gives an invariant answer, even with reuse0; it does not identify the cause of the ordinal-dependent differences.

## Sampled verify columns

The two originally planned sampled processes (`sampled-cols-check`, `sampled-old-cols`) used the **threaded q4x split** verify-window branch. Source review and the absence of checker lines showed that `verify_sample` delegates through `next_port_` to `part_window_sample`, which calls the old `fast_sample` directly. Both sampler flags were inactive there. All four paired 2,048-ID responses and draft accepted/offered counts match across those starts: **True**. This is request-sequence repeatability evidence only, not validation of the new sampler.

The first written coverage amendment tried `STRATA_GLM_NO_SPEC=1` on split 32, based on an incorrect initial assumption that the original run used pipelined `decode_spec`. The code and native `ds4 dspark` lines showed that both split cases already used the threaded verify-window route, whose tail sampling still bypasses the new sampler. We stopped only our probe master once that became clear and restored its services. Its full captured stdout, response record, audits, termination reason and first amendment remain in the archive, separately excluded from the primary comparisons. The second planned split control was never launched. The probe emitted two full 2,048-ID responses / DONE lines; the client saved one per-response JSON before interruption. Both full native sequences are retained in the raw stdout and extracted in results.json. Neither is included in the primary comparisons.

A second written amendment selected **single physical 5070 Ti**, with no layer split or next-port delegation. The same unmodified v117 binary, original IQ3_S/RTMTP assets, prior, CPU 0 deterministic settings, seed and other limits are used, including `STRATA_GLM_NO_SPEC=1` in both controls. This changes GPU residency and is not compared in speed or output identity with split 32. Each single-GPU process runs one full warmup plus three diagnostic requests, temperature 1.0:

1. `single-sampled-cols-check`: default batched sampler with `STRATA_GLM_SAMPLE_COLS_CHECK=1`; each consumed column is also drawn with the old sampler using the same logits/counter.
2. `single-sampled-old-cols`: old column-at-a-time sampler with `STRATA_GLM_SAMPLE_COLS=0`, checker off.

Actual checker lines, rather than flag presence, establish coverage in the single-GPU case. All original and stopped-probe records remain in the package; no outcome-based subset was selected.

- Checker maximum logged columns: **5632**, differing draws: **0**. The checker logs every 256 columns, so its final printed count is a lower bound; it does not prove every unconsumed speculative column was checked.
- All four paired 2,048-ID responses match between new/old sampler paths: **True**.
- Raw checker lines, draft counters, complete output IDs and any first differing position are retained for every pair.

This is a same-version path comparison. It does not settle the historical v109/v111 token-0 observation, establish general determinism across hardware/builds or prove model accuracy.

## Resource and restoration evidence

Six completed primary processes,22responses (6warmups and16other diagnosticresponses), plus one stopped split coverage probe with two full native responses retained separately (24 native DONE responses overall). Coverage amendments are described above; there was no outcome-based retry or best-result selection. The shared GPU lock covered each of three service-pause/build/diagnostic cycles; it was released between the original and amended cycles. Before stopping the two authorized GPU services, their queues were empty and idle CPU/GPU samples passed. CPU/IO/RSS and global NVMe audits started before model load/calibration and ran through engine exit; temperature, thermal slowdown, RAM and swap guards stopped only our processes on failure.

| Process | Responses | Audit samples | Max independent CPU cores | Max independent physical IO MiB/s | Peak GPU temperatures C |
|---|---:|---:|---:|---:|---|
| deterministic-greedy-start01 | 3 | 70 | 0.0195 | 0.0000 | {'0': 62.0, '1': 64.0} |
| deterministic-greedy-start02 | 3 | 68 | 0.0147 | 0.0000 | {'0': 60.0, '1': 65.0} |
| sampled-cols-check | 4 | 92 | 0.0098 | 0.0000 | {'0': 63.0, '1': 66.0} |
| sampled-old-cols | 4 | 92 | 0.0049 | 0.0000 | {'0': 64.0, '1': 66.0} |
| single-sampled-cols-check | 4 | 125 | 0.0098 | 0.0000 | {'0': 63.0, '1': 42.0} |
| single-sampled-old-cols | 4 | 125 | 0.0146 | 0.0000 | {'0': 63.0, '1': 37.0} |

All accepted audits have no contention reasons, and GPU compute PIDs belong only to this run while services are paused. Sampling about every 2 seconds cannot exclude every brief event or unreadable process detail. Source/binary hashes and original model sizes/mtimes were verified after exit. No fresh full-weight hash was run during diagnostics; small metadata hashes and the prior weight identity are retained. Both previously active GPU services and their GPU reservations were restored, our engines exited and the shared lock was verified free. No other job, service, power/clock/fan setting or OS updater was changed.

The archive contains unabridged stdout/stderr including startup, INFO/READY/PP/T/STAT/DONE and exit logs, checker lines, exact fixtures/output IDs/settings, host audits and telemetry, pinned source review, build commands/log/provenance, harness, model preservation and service restoration proofs. Private paths/IPs/process identifiers are redacted. No model weights are included.
