Abyss Issue #24: v1.3.102 per-stage prefill profiling

Author request: https://github.com/zephel01/Abyss/issues/24#issuecomment-6594935052

Selected **profile-01 (slow)** and **profile-04 (fast)** under the recorded rule. The largest stage increase is **moe_staged**: 9449.8 versus 3294.6 ms, **2.868×**, contributing **100.7%** of the 6112.6 ms summed stream-time difference. This localizes the observed growth to a native phase label; it does not identify a root cause, an individual kernel or a per-expert cost. A share above 100% means other stages offset some of this increase.

| Process | State | Whole-16K Prefill tok/s, all three requests | Profiled stream ms | moe_staged ms | v41_attn ms |
|---|---|---|---:|---:|---:|
| profile-01 | slow | 1941.1 / 1995.4 / 2076.4 | 23969 | 9449.8 | 2474.1 |
| profile-02 | slow | 2018.6 / 2066.7 / 2082.9 | 23512 | 9343.8 | 2477.6 |
| profile-03 | slow | 2034.3 / 2073.7 / 2082.5 | 23429 | 9318.0 | 2478.2 |
| profile-04 | fast | 2683.4 / 2699.5 / 2698.3 | 17856 | 3294.6 | 2480.4 |

| Native stage | Slow ms | Fast ms | Slow/fast | Delta ms | Share of stream-time delta |
|---|---:|---:|---:|---:|---:|
| moe_staged | 9449.8 | 3294.6 | 2.868× | +6155.2 | 100.7% |
| engram | 1215.2 | 935.9 | 1.298× | +279.3 | 4.6% |
| hc | 955.3 | 908.6 | 1.051× | +46.7 | 0.8% |
| v41_proj | 229.7 | 198.6 | 1.157× | +31.1 | 0.5% |
| dsa | 0.3 | 0.8 | 0.375× | -0.5 | -0.0% |
| shexp | 1105.6 | 1107.1 | 0.999× | -1.5 | -0.0% |
| moe_light | 269.2 | 272.7 | 0.987× | -3.5 | -0.1% |
| v41_index | 1546.9 | 1551.5 | 0.997× | -4.6 | -0.1% |
| route | 28.0 | 33.6 | 0.833× | -5.6 | -0.1% |
| v41_attn | 2474.1 | 2480.4 | 0.997× | -6.3 | -0.1% |
| router | 162.5 | 169.8 | 0.957× | -7.3 | -0.1% |
| combine | 102.7 | 110.5 | 0.929× | -7.8 | -0.1% |
| v41_q | 643.4 | 657.0 | 0.979× | -13.6 | -0.2% |
| v41_out | 1261.4 | 1285.2 | 0.981× | -23.8 | -0.4% |
| moe_prestaged | 1848.9 | 1915.1 | 0.965× | -66.2 | -1.1% |
| plan | 618.6 | 727.5 | 0.850× | -108.9 | -1.8% |
| moe_resident | 2057.5 | 2207.6 | 0.932× | -150.1 | -2.5% |

Exit-profile counters for slow/fast: **49,149 / 49,149 profiled tokens**; disk waits **0 / 0 ms**; host plan **18 / 30 ms**; disk experts used/read **0/0 / 0/0**. The input is 49,152 token IDs per process; the profiler's own token counter is reported separately.

Ran **4 fresh processes**, all with **STRATA_GLM_PREFILL_PROF=1**, helper ON / PROMOTE=0 / **RESYNC=0**. Each runs the same original trial-01 16K input **three times with 2K generation**, greedy/seed42, reuse disabled. The process-exit profile sums **all three prompts, including the first warm-up**. This is a diagnostic run; I did not mix these instrumented timings into the earlier clean speed results. A predeclared maximum of six processes stops as soon as one stable slow (<2300 tok/s for all three prompts) and one stable fast (>2500 for all three) are present. Every process and request is retained. Selected cases are the first qualifying ones, not the most extreme. The separately predeclared two unprofiled controls were not triggered because a fast profiled process was found.

Same v1.3.102 commit e4eaf01f089a3e7fb2621720fac17e5cb241c223 and exact previously tested binary (SHA256 42ac81a4724fe30b7e6bc08b5d5b44c0c1025d5cb5d28ee5302f11a6380422d0), copied into an isolated test directory. No rebuild for this runtime flag. The current main update 3705d81 is documentation only. Same optional MXFP8 reader adapter; no local prefill/helper changes. Same unsplit IQ2_XS + Huihui + MXFP8 target, DSpark Q2K-Q4K enabled; PRO5000 72GB primary / PRO4500 32GB helper, Gen5 x8 each, CUDA_VISIBLE_DEVICES=1,0, helper cap28GiB, CPU lane12, RAM128 decimal GB, context32768, chunk4096. Only the new profiler flag is added relative to the existing helper-ON/PROMOTE0/RESYNC0 configuration.

These are CUDA-event intervals accumulated under the engine phase names, not pure individual-kernel times. They can include GPU-stream stalls and do not sum to end-to-end request wall time. The profiler adds events and synchronization; no uninstrumented-versus-instrumented overhead claim is made. The rule searches for states, so these samples do not estimate their frequency. Generated output IDs vary; no new numerical CHECK or full-model accuracy comparison. Whole-prompt rates use DONE prompt_ms, not the first-4K PP prefix. The final STAT before each DONE is used for native Decode checks.

No helper fallbacks, resync work, thermal-slowdown flags or resource-guard trips. Peak helper/primary temperatures **55/83 C**. Pack metadata hashes, model sizes/mtimes and running user services unchanged. Test processes exited and our runner released its GPU lock. Preservation does not hash every model weight.

The archive contains complete stdout/stderr from every process, all process-exit profiles, both reader timelines, telemetry, exact input fixtures/settings, request metrics/output IDs, the harness and predeclared sampling policy, source/adapter and binary hashes, the original build receipts and binary-reuse proof, and before/after preservation receipts. Stdout retains all T/STAT/PP/READY/DONE records; timelines omit T only. Private home prefixes are redacted; no model weights, credentials, private IPs or GPU UUIDs are included.

Archive SHA256: 063485cbe64ec4a8798552a420854de2dc9489b8d4f08aab50bb3f0bd012f36e
Archive entries: 59
