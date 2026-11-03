Abyss Issue #24: isolated v1.3.102 VERBOSE and CPU=0 revalidation

Author request: https://github.com/zephel01/Abyss/issues/24#issuecomment-6595998811

**The slow state still occurs in the isolated rerun.** In default-02, all three prompts assigned **zero experts to the host**, with kappa **1.00 / 1.00 / 1.00** and row cost **0.050 / 0.050 / 0.050 ms**. The fast default-01 used the host on every prompt, with kappa **0.70 / 0.53 / 0.53**. Both startup CPU calibrations were in the normal range (0.160/0.155 ms/expert), with the same logged CPU-take table. No competing heavy work was detected.

**PREFILL_CPU=0:** three fresh processes, all verified to report zero host experts/rows/time. Whole-16K rates span **2036.3–2079.6 tok/s** in these nine prompts. The no-host runs occupy the same low-speed band as the default slow process. Thus CPU=0 did not remove that band here; it also did not produce a second, faster CPU=0 state in this small sample. Since the default slow process was already doing no host work, these results alone do not establish a PCIe-copy fault. The direct observed difference is whether the default prompt plan actually uses the host.

| Process | Prefill CPU | Whole-16K Prefill tok/s, three requests | CPU calibration ms/expert | PCIe calibration ms/expert |
|---|---|---|---:|---:|
| default-01 | default | 2667.1 / 2729.5 / 2726.1 | 0.155 | 0.342 |
| default-02 | default | 2038.4 / 2077.5 / 2080.1 | 0.160 | 0.342 |
| cpu0-01 | cpu0 | 2036.5 / 2076.9 / 2079.6 | 0.155 | 0.342 |
| cpu0-02 | cpu0 | 2036.3 / 2075.2 / 2078.0 | 0.155 | 0.342 |
| cpu0-03 | cpu0 | 2036.6 / 2075.0 / 2078.5 | 0.155 | 0.342 |

| Process | Host experts per request | Kappa after each request | CPU row ms after each request | RAM-staged experts, final cumulative | Prestaged experts, final cumulative |
|---|---|---|---|---:|---:|
| default-01 | 5987 / 5833 / 5671 | 0.70 / 0.53 / 0.53 | 0.016 / 0.016 / 0.019 | 12298 | 13375 |
| default-02 | 0 / 0 / 0 | 1.00 / 1.00 / 1.00 | 0.050 / 0.050 / 0.050 | 31728 | 11346 |
| cpu0-01 | 0 / 0 / 0 | 1.00 / 1.00 / 1.00 | 0.050 / 0.050 / 0.050 | 31728 | 11346 |
| cpu0-02 | 0 / 0 / 0 | 1.00 / 1.00 / 1.00 | 0.050 / 0.050 / 0.050 | 31728 | 11346 |
| cpu0-03 | 0 / 0 / 0 | 1.00 / 1.00 / 1.00 | 0.050 / 0.050 / 0.050 | 31728 | 11346 |

| Native GPU-stream phase, sum over three prompts | Slow ms | Fast ms | Slow/fast |
|---|---:|---:|---:|
| moe_staged | 9326.4 | 3258.5 | 2.862× |
| moe_prestaged | 1780.6 | 1853.5 | 0.961× |
| moe_resident | 2202.7 | 2182.1 | 1.009× |
| v41_attn | 2476.7 | 2471.2 | 1.002× |

| Process | Host audit samples | Max independent CPU cores | Max independent physical IO MiB/s |
|---|---:|---:|---:|
| default-01 | 62 | 0.0049 | 0.0019 |
| default-02 | 64 | 0.0049 | 0.0019 |
| cpu0-01 | 63 | 0.0049 | 0.0019 |
| cpu0-02 | 63 | 0.0049 | 0.0019 |
| cpu0-03 | 63 | 0.0049 | 0.0019 |

Pinned **v1.3.102 / `e4eaf01f089a3e7fb2621720fac17e5cb241c223`**, same previously tested binary SHA256 `42ac81a4724fe30b7e6bc08b5d5b44c0c1025d5cb5d28ee5302f11a6380422d0`; at the start of this batch main's later 3705d81 commit was docs only; v1.3.103 arrived afterward and is checked separately. No new build or local engine change. Same optional MXFP8 reader adapter. Same unsplit IQ2_XS + Huihui + MXFP8 target, DSpark Q2K-Q4K, PRO5000 72GB primary / PRO4500 32GB helper, Gen5 x8 each; CUDA_VISIBLE_DEVICES=1,0, helper28GiB, CPU lane12, RAM128 decimal GB, context32768, chunk4096, greedy/seed42, reuse0, helperON/PROMOTE0/RESYNC0.

All 5 processes are fresh, each with the identical original trial-01 input repeated **three times at 16K input / 2K generation** (15 requests total). Both PROF=1 and VERBOSE=1 are enabled throughout. Default CPU share leaves PREFILL_CPU unset; the ablation adds only PREFILL_CPU=0. This flag disables host sharing in prompt processing; Decode's CPU lane remains configured. The default search was capped at six and stopped at the first stable slow/fast pair; the CPU=0 group has exactly three processes. Every process/request is retained. Process-exit profiles include the first warm-up and both later requests.

The other conversion and speed-measurement task completed before this batch. The exclusive shared-machine lock was held for the entire sequence. Before every engine launch, a read-only host audit collected at least four samples and waited for three consecutive quiet NVMe intervals. The same-user process CPU/IO/RSS audit and all-GPU-compute checks continued through model load, CPU calibration, prompts and exit, alongside temperature/RAM/swap monitoring. Contention would terminate only our engine. Thresholds and the complete audit are in the archive; no independent build/conversion or other GPU process was detected. Sampling is approximately two seconds and cannot exclude every brief OS event. Small independent CPU/IO entries include read-only status collection.

The verbose host/staged/prestage counters are cumulative within each process. The host-expert column above is the per-request increment; kappa and row cost are the learned values printed after each prompt. Exact native lines and all cumulative counters are provided. The profiler reports 49,149 batched tokens per process; 49,152 input token IDs were submitted. Whole-prompt rates use DONE prompt_ms for all 16,384 input tokens, rather than the first-4K PP prefix.

These are instrumented diagnostics, not a clean throughput or full-model accuracy comparison. CUDA-event phase totals include stream stalls and are not pure per-kernel/per-expert timings. Output token IDs vary. The small, state-seeking sample does not establish state frequencies or a complete root cause. No new numerical CHECK run. The earlier CPU-build-overlapped profile remains provisional; the observations here are from the separately audited rerun.

No helper fallback, resync work, thermal-slowdown flag or resource-guard trip. Peak helper/primary temperatures **55/83 C**. Pack metadata hashes, model sizes/mtimes and running user services were preserved; our test processes exited and released the lock. No power, clock, fan or service settings were changed.

The archive includes complete stdout/stderr and process-exit profiles from every run, exact split-kappa lines, startup calibration/tier records, both reader timelines, per-process host-activity audits, GPU/resource telemetry, settings/input IDs/output IDs, the harness/host-audit module and predeclared policy, source/adapter/binary hashes, original build/binary-reuse receipts, and before/after preservation records. Private home prefixes are redacted; no weights, credentials, private IPs or GPU UUIDs are included.

Archive SHA256: 62d210884e79740aed8b1aa122c33fe77023c51ba8243871466e70a09d8068d9
Archive entries: 76
