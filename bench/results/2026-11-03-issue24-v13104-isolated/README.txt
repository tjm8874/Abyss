Abyss Issue #24: v1.3.104 prompt CPU-share gate verification

Author request: https://github.com/zephel01/Abyss/issues/24#issuecomment-6598429197

Four fresh processes, all retained: whole-16K Prefill 2691.2–2729.3 tok/s across all 12 prompts; non-zero host assignments on 12/12 prompts. Low-band fresh processes: 0/4.

| Fresh process | Whole-16K Prefill tok/s, three requests | Decode tok/s, three requests | CPU / PCIe calibration ms/expert | Host experts per request | Kappa after each prompt | CPU row ms after each prompt |
|---|---|---|---|---|---|---|
| default-01 | 2705.9 / 2720.2 / 2729.3 | 83.3 / 101.9 / 103.0 | 0.155 / 0.342 | 5993 / 5749 / 5705 | 0.71 / 0.52 / 0.50 | 0.018 / 0.015 / 0.014 |
| default-02 | 2704.5 / 2714.4 / 2714.1 | 87.5 / 102.3 / 96.0 | 0.155 / 0.342 | 6030 / 5865 / 5762 | 0.69 / 0.50 / 0.49 | 0.016 / 0.015 / 0.013 |
| default-03 | 2693.3 / 2715.1 / 2705.1 | 84.4 / 101.6 / 103.3 | 0.155 / 0.342 | 6015 / 5832 / 5671 | 0.68 / 0.53 / 0.55 | 0.015 / 0.018 / 0.024 |
| default-04 | 2691.2 / 2706.7 / 2704.5 | 86.8 / 100.8 / 101.9 | 0.155 / 0.342 | 5981 / 5831 / 5680 | 0.69 / 0.51 / 0.51 | 0.016 / 0.016 / 0.018 |

Calibration retry/busy lines: 0. CPU_CAL_RETRY was omitted (default3); no artificial competing load was introduced. The CPU timings span 0.155–0.155 ms/expert; this sample does not deliberately force a timing near the former gate boundary or validate the busy-retry path.

TAIL_ON_TOP was omitted (default1). The full-model-fit tail-on-top message appeared in 0 processes. This target does not fit wholly on the primary card, so this is not a validation of the separate all-VRAM-model tail-layout optimization.

Pinned v1.3.104 / 3f05905cabac26e0a665671c1f72106584e7c21f; fresh engine SHA256 c23b8854d35119e5f10b47921dd6a89073e0b4c52a11f86fa69b893564db7671. Official source plus the unchanged optional MXFP8 reader adapter c2c26136fe086b4a1641e4c70878baa0eb8508fa2bbebc835cad54b3e76390ff, with no local prompt/helper/calibration changes. The build held the shared machine lock and finished before testing. The code removes the startup CPU-vs-PCIe speed gate in glm_prefill.cu; the release also changes full-fit tail placement.

Same unsplit ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention replacements + MXFP8 Engram, DSpark Q2K-Q4K enabled. PRO5000 72GB primary + PRO4500 32GB helper, PCIe Gen5 x8 each; CUDA_VISIBLE_DEVICES=1,0, helper cap28GiB, PROMOTE0/RESYNC0, CPU lane12, RAM128 decimalGB, context32768/chunk4096, greedy seed42, reuse disabled. STRATA_GLM_PREFILL_PROF=1 and VERBOSE=1; PREFILL_CPU omitted/default. Same original trial-01 input repeated three times per process, SHA256 13f9df432a5568ac5ea8aed610a9949e27414abf94ad73b414181bf8a1e8de1a. Exactly16,384 input/2,048 output IDs each. Whole-prompt rates use DONE.prompt_ms, not the first4K PP prefix. Host counters in native VERBOSE lines are cumulative; the table shows per-request increments.

Predeclared fixed four fresh starts, three identical requests each, no early stop for favorable speed. First request is the warm-up; all three are shown and included in each process-exit profile. Sampling is bounded, not proof that all future starts will be fast. These instrumented diagnostics are not a clean throughput ranking or an accuracy comparison; output IDs may differ, no new numerical CHECK run, no CPU0 or synthetic busy-load run.

The exclusive shared-machine lock was held during the sequence. The same read-only host audit waits for at least four samples/three consecutive quiet NVMe intervals before every Popen, then checks same-user process CPU/IO/RSS and all GPU compute processes through load, calibration, requests and exit. Thermal/RAM/swap guards run alongside it. Contention stops only our own engine. Sampling is about2s and cannot exclude every brief OS event or inaccessible process detail. Full audits, thresholds, native startup/STAT/profile records and build provenance are in the archive.

| Process | Host-audit samples | Max independent CPU cores | Max independent physical IO MiB/s |
|---|---:|---:|---:|
| default-01 | 61 | 0.0049 | 0.0019 |
| default-02 | 61 | 0.0049 | 0.0019 |
| default-03 | 61 | 0.0049 | 0.0019 |
| default-04 | 61 | 0.0049 | 0.0019 |

Peak helper/primary temperatures 54/83 C. No detected competing heavy work, helper fallback, resync work, thermal-slowdown flag or resource-guard trip. Pack metadata hashes, model sizes/mtimes and running user services preserved; own GPU processes exited and shared lock released. No service, power, clock or fan settings changed. Preservation does not hash every model weight.

Archive includes complete unabridged stdout/stderr, all output IDs, STAT/PP/READY/DONE/glm stat lines, full native calibration and learned split lines, process-exit profiles, both timelines, host-activity audits, telemetry and guards, exact settings/input fixtures, harness/audit/fixed policy, full build logs/options/commands, source/adapter/binary hashes and preservation receipts. Private home paths redacted; no model weights, credentials, private IPs or GPU UUIDs.
Archive SHA256: 6b8f6d82c15e16bde86d2b5063dc726b29512f7f24cae99f95f29538919564b5
Archive entries: 67
