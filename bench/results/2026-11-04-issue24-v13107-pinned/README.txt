Abyss Issue #24: v1.3.107 default prompt share and configured pin-cap fallback

Trigger: relevant v1.3.107 CPU pinned-buffer handling update; no new Issue24 author request.
Related report: https://github.com/zephel01/Abyss/issues/31
Prior Issue24 acceptance: https://github.com/zephel01/Abyss/issues/24#issuecomment-6599783710

Three normal fresh starts: whole-16K Prefill 2649.8–2727.4 tok/s across nine prompts; non-zero host assignments on 9/9 prompts. Normal pin-failure messages: 0.

Configured PIN_MB=64: all three16K/2K requests completed, one pin-failure warning for the process, zero prompt host experts throughout; Prefill 2038.0 / 2077.1 / 2088.4 tok/s. Explicit PREFILL_CPU=0 control: all three completed, zero host experts and no pin-failure message; 2036.8 / 2075.9 / 2087.5 tok/s.

| Fresh process | Mode | Whole-16K Prefill tok/s, three requests | Decode tok/s, three requests | CPU / PCIe calibration ms/expert | Host experts per request | Kappa after each prompt | Pin-failure log lines |
|---|---|---|---|---|---|---|---:|
| default-01 | default | 2649.8 / 2727.4 / 2725.9 | 81.4 / 99.1 / 100.1 | 0.155 / 0.342 | 6006 / 5770 / 5690 | 0.69 / 0.55 / 0.54 | 0 |
| default-02 | default | 2679.8 / 2699.0 / 2717.7 | 84.3 / 100.7 / 102.8 | 0.155 / 0.342 | 6019 / 5813 / 5688 | 0.68 / 0.52 / 0.52 | 0 |
| default-03 | default | 2673.2 / 2699.1 / 2704.2 | 83.4 / 99.2 / 103.5 | 0.160 / 0.342 | 6066 / 5808 / 5708 | 0.70 / 0.52 / 0.50 | 0 |
| pin64-01 | pin64 | 2038.0 / 2077.1 / 2088.4 | 85.1 / 100.2 / 102.8 | 0.155 / 0.342 | 0 / 0 / 0 | 1.00 / 1.00 / 1.00 | 1 |
| cpu0-01 | cpu0 | 2036.8 / 2075.9 / 2087.5 | 85.4 / 101.6 / 103.2 | 0.155 / 0.342 | 0 / 0 / 0 | 1.00 / 1.00 / 1.00 | 0 |

Native configured-cap warning:
glm prefill: the CPU lane's pinned host buffers did not allocate (91785 MB of RAM free) - prompts stage every expert over PCIe from here on (as STRATA_GLM_PREFILL_CPU=0)

Natural startup boundary observation: default-03 calibrated at >=0.159 ms/expert and still used the host on every prompt; exact native lines are included.
Calibration retry/busy lines: 0. No artificial competing load.

Pinned v1.3.107 / 0632d5e48d439693e58eabe9bd402386251d492d; fresh engine SHA256 d9e44b1a92657d3eea483a7d312b8bf95303cc76db711abb66b41e23ff5451fc. Official source plus unchanged optional MXFP8 reader adapter c2c26136fe086b4a1641e4c70878baa0eb8508fa2bbebc835cad54b3e76390ff. No local CPU-allocation/prefill/helper/calibration patch. The shared lock was held for the build, which completed before testing. Source review confirms pinned buffers are acquired before host assignment, a cap/refusal sets process-persistent pin_fail, and subsequent prompt experts are staged over PCIe.

Same unsplit ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention replacements + MXFP8 Engram, DSpark Q2K-Q4K enabled. PRO5000 72GB primary + PRO4500 32GB helper, PCIe Gen5 x8 each; CUDA_VISIBLE_DEVICES=1,0, helper cap28GiB, PROMOTE0/RESYNC0, CPU lane12, RAM128 decimalGB, context32768/chunk4096, greedy seed42, reuse disabled. PREFILL_PROF=1 and PREFILL_VERBOSE=1 throughout. Normal mode omits both PREFILL_CPU and PREFILL_PIN_MB; pin64 sets only PREFILL_PIN_MB=64; cpu0 sets only PREFILL_CPU=0. CPU_CAL_RETRY omitted/default3. Same original trial-01 IDs repeated three times in each process, SHA256 13f9df432a5568ac5ea8aed610a9949e27414abf94ad73b414181bf8a1e8de1a; exactly16,384 input /2,048 output IDs per request. Whole-prompt rates use DONE.prompt_ms, not the first4K PP prefix. Host counts shown are per-request increments of cumulative native counters.

Predeclared fixed five fresh starts: three default, one pin64 and one CPU0; three identical requests each,15 total, no early stop for favorable speed. First request is the warm-up; all requests are shown and included in process-exit profiles. The cap deliberately refuses CPU prompt buffers; it does not exhaust system RAM, reproduce the original Windows cudaHostAlloc failure/crash, or exercise growth of a previously allocated host buffer. Linux, fixed16K inputs/chunk4096/context32768; no20K/40K/89K Windows or larger-context claim. No new numerical CHECK or accuracy test. Generated output IDs may differ; instrumented diagnostics are not a clean throughput/quality ranking. The v106 IQ1_S/Qwen-MTP changes and HTTP end guard are not exercised by this IQ2_XS native GEN recipe (no end_guard/think_end keys).

The native exit profiler counts 49,149 batched tokens per process;49,152 input IDs were submitted. Whole-prompt rates use all16,384 IDs in DONE.

The exclusive shared-machine lock covered the sequence. Before each Popen the read-only host audit waits for at least four samples and three consecutive quiet NVMe intervals, then samples same-user process CPU/IO/RSS plus all GPU compute processes through loading, calibration, requests and exit. Thermal/RAM/swap guards remain active. Contention stops only our engine. Sampling is about2s and cannot exclude every brief OS event or inaccessible process detail.

| Process | Host-audit samples | Max independent CPU cores | Max independent physical IO MiB/s |
|---|---:|---:|---:|
| default-01 | 63 | 0.0099 | 0.0039 |
| default-02 | 61 | 0.0098 | 0.0039 |
| default-03 | 61 | 0.0049 | 0.0039 |
| pin64-01 | 63 | 0.0049 | 0.0039 |
| cpu0-01 | 63 | 0.0049 | 0.0039 |

Peak helper/primary temperatures 56/83 C. No detected external heavy work, helper fallback, resync work, thermal-slowdown flag or resource-guard trip. The intentional CPU prompt fallback is separate from helper fallbacks. Pack metadata hashes, model sizes/mtimes and running user services preserved; own GPU processes exited and shared lock free. Power/clock/compute-mode readback unchanged; no fan/service settings changed. Preservation does not hash every model weight.

Archive includes unabridged stdout/stderr and native STAT/glm stat, exact settings/input IDs/output IDs, complete profile/calibration/split logs and timelines, host audits and GPU/resource telemetry, harness/policy, source/adapter/binary hashes, full build log/options/commands, cleanup/preservation receipts. Private home prefixes redacted; no weights, credentials, private IPs or GPU UUIDs.
Archive SHA256: 3b09b9dedbd388bf5a483d1efd9c3af2f25dae64aeecdc1abdd22722e36cd236
Archive entries: 78
