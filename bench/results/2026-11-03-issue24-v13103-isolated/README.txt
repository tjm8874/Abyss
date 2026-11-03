Abyss Issue #24: quiet v1.3.103 follow-up after isolated v102 diagnostics

Author comment: https://github.com/zephel01/Abyss/issues/24#issuecomment-6596709680

The two quiet v1.3.103 starts did not show the low-speed band in this small sample. This does not establish that the intermittent prompt-planning state is fixed.

| v1.3.103 process | Whole-16K tok/s, three requests | CPU / PCIe calibration ms/expert | Host experts per request | Kappa after each prompt | CPU row ms after each prompt |
|---|---|---|---|---|---|
| default-01 | 2709.5 / 2733.9 / 2708.2 | 0.155 / 0.342 | 5958 / 5884 / 5731 | 0.70 / 0.54 / 0.51 | 0.017 / 0.018 / 0.016 |
| default-02 | 2694.5 / 2708.3 / 2710.0 | 0.155 / 0.342 | 5980 / 5817 / 5686 | 0.69 / 0.52 / 0.52 | 0.016 / 0.018 / 0.016 |

Neither quiet start emitted a calibration-disturbed or still-busy message. CPU_CAL_RETRY was omitted, using the new default of 3; no retry was observed.

| Process | Host-audit samples | Max independent CPU cores | Max independent IO MiB/s |
|---|---:|---:|---:|
| default-01 | 61 | 0.0049 | 0.0019 |
| default-02 | 60 | 0.0049 | 0.0019 |

Fresh build of **v1.3.103 / b80756674b469a877f4764635056bc581676ad58**, engine SHA256 **7e1ac91a5112c2fe1b8caba615b9bcd283413a2cb3dbe0f7dd028b6b3d3c9740**. The upstream inference-code change is confined to CPU startup calibration in glm_fast_path.cu; glm_prefill.cu is unchanged from the earlier v102 test. Same optional MXFP8 reader adapter, with no local calibration/helper/prefill patch. The build itself held the shared machine lock and completed before testing. No intentional competing CPU load was introduced, so this checks the quiet-start behavior and does not validate the busy-retry path.

Exactly two fresh default-CPU-share processes, three identical trial-01 16K/2K requests each. PROF1/VERBOSE1/helperON/PROMOTE0/RESYNC0, same CVD1,0, 28GiB helper, CPU12, RAM128 decimal GB, context32768, chunk4096, greedy seed42 and no reuse. The same pre-launch and through-exit host CPU/IO/RSS/GPU audit and thermal/resource guards as the isolated v102 batch are used. All data are retained. Process-exit profiles include the first warm-up.

Two starts are a bounded follow-up, not an occurrence-rate estimate or a clean speed/quality comparison. The profiler is instrumented and phase times are GPU-stream intervals. Host audit is sampled at about two seconds and cannot exclude every brief OS event. The three v102 CPU=0 ablations are separate evidence, not v103 runs.

Peak helper/primary temperatures 52/81 C; no detected contention, fallback, resync work, thermal slowdown or resource trip. Pack metadata hashes, model sizes/mtimes and running user services preserved; own test processes and lock released. No power/clock/fan settings changed.

Archive contains complete stdout/stderr, process-exit profiles, split-kappa and calibration lines, timelines, host-activity audits and GPU telemetry, exact settings/fixtures/output IDs, harness/audit/policy files, full build log/options/commands and source/adapter/binary hashes, and before/after preservation receipts. Private home prefixes redacted; no model weights or credentials.
Archive SHA256: 3ceadee9f2ff5bad54487bd4f2a6a1de0426cb9adbddf34e3d2b3ac7018563bb
Archive entries: 43
