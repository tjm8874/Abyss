Abyss Issue #24: v1.3.108 MMQ expert-slot padding validation

The old v107 normal starts logged the MMQ slot-overread warning 3 times across three fresh processes. The v108 validation logs it 0 times across four fresh processes, including the separate numerical diagnostic. Normal v108 Prefill is 2666.9–2729.5 tok/s across nine16K/2K requests; non-zero host experts on 9/9.

| Normal fresh process | Whole-16K Prefill tok/s, three requests | Decode tok/s, three requests | CPU / PCIe calibration ms/expert | Host experts per request | MMQ slot-overread warnings |
|---|---|---|---|---|---:|
| default-01 | 2702.1 / 2727.6 / 2728.3 | 83.4 / 100.3 / 103.7 | 0.155 / 0.342 | 6073 / 5794 / 5678 | 0 |
| default-02 | 2666.9 / 2704.4 / 2717.4 | 85.1 / 101.6 / 100.8 | 0.162 / 0.342 | 6023 / 5817 / 5807 | 0 |
| default-03 | 2674.5 / 2715.0 / 2729.5 | 84.7 / 100.6 / 105.9 | 0.154 / 0.342 | 6018 / 5814 / 5731 | 0 |

Separate lightcheck-01 with STRATA_GLM_PREFILL_LIGHT_CHECK=1: 180 native row-comparison records across 16 layers, 180 finite records and 0 non-finite records. Relative L2 ranges 3.586e-04–2.229e-03; maximum per-record worst-row relative L2 6.130e-03. The checker reruns eligible light expert rows through MMQ; it is a partial kernel comparison with quantized activation paths, not an end-to-end logits/token reference or a model-accuracy score. No arbitrary numerical pass tolerance was imposed. Its timings are excluded from the normal-speed table.

Pinned v1.3.108 / 1c302cedfee31a03ea47a197fb0c18ba7fe0e5e1; fresh engine SHA256 7b8cdc9348cc2f546e54e3a063c0e3324e338f5c26d0e1f630729c9818614e17. Official source plus unchanged optional MXFP8 reader adapter c2c26136fe086b4a1641e4c70878baa0eb8508fa2bbebc835cad54b3e76390ff. No local prefill/padding/helper/calibration patch. The build held the shared lock and completed before measurements. Source review: expert_stride now reserves the down-MMQ over-read when alignment padding was insufficient; all allocation/prefill/search callers pass the expert width. The other release change is the Python HTTP thinking-budget reserve and is not exercised by native pre-encoded GEN requests with2048 generated tokens/no think_end or think_budget keys.

Same unsplit ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention replacements + MXFP8 Engram, DSpark Q2K-Q4K enabled. PRO5000 72GB primary + PRO4500 32GB helper, PCIe Gen5 x8 each; CUDA_VISIBLE_DEVICES=1,0, helper28GiB, PROMOTE0/RESYNC0, CPU lane12, RAM128 decimalGB, context32768/chunk4096, greedy seed42, reuse disabled. PREFILL_PROF1/VERBOSE1 in all cases; PREFILL_CPU/PIN_MB omitted. LIGHT_CHECK only on the separate diagnostic process. Same original trial-01 IDs repeated three times in each process, input SHA25613f9df432a5568ac5ea8aed610a9949e27414abf94ad73b414181bf8a1e8de1a,16384 input/2048 output IDs per request. Rates use whole-prompt DONE.prompt_ms, not the first4K PP prefix. Table host counts are per-request increments of cumulative native counters.

Predeclared fixed three normal fresh processes plus one separate numerical diagnostic, three identical requests per process,12 total. First request is the warm-up; all requests and output IDs are retained. Exit profiles include all three; the engine counts 49,149 batched tokens versus49,152 input IDs submitted per process. No early stopping or selection for speed. Normal samples retain PROF/VERBOSE instrumentation; this is not an uninstrumented throughput ranking. Output IDs can differ. Warning removal alone does not prove prior output was wrong or establish full-model numerical/quality equivalence. No Qwen3.8 model, small-output HTTP budget or helper-CHECK test was added.

The exclusive shared-machine lock covered the sequence. Before each Popen, at least four audit samples and three consecutive quiet NVMe intervals; same-user process CPU/IO/RSS and all GPU compute processes are sampled through loading, calibration, requests and exit. Temperature/RAM/swap guards remain active and stop only our engine on contention. About2s sampling cannot exclude every brief OS event or inaccessible process detail.

| Process | Mode | Host-audit samples | Max independent CPU cores | Max independent physical IO MiB/s |
|---|---|---:|---:|---:|
| default-01 | default | 61 | 0.0049 | 0.0058 |
| default-02 | default | 61 | 0.0049 | 0.0038 |
| default-03 | default | 60 | 0.0098 | 0.0019 |
| lightcheck-01 | lightcheck | 60 | 0.0098 | 0.0019 |

Peak helper/primary temperatures 55/84 C. No detected external heavy work, helper fallback, pin-failure warning, resync work, thermal-slowdown flag or resource-guard trip. Pack metadata hashes, model sizes/mtimes and running user services preserved; own GPU processes exited and shared lock free. Power/clock/compute-mode readback unchanged; fan/service settings not changed. Preservation does not hash every model weight.

Archive contains unabridged stdout/stderr including native comparison lines, all STAT/PP/READY/DONE/glm stat and output IDs, profiles/calibration/split records, both timelines, host/GPU/resource audits, exact inputs/settings, harness/fixed policy, full build provenance/source/adapter/binary hashes, prior-warning observation and preservation/cleanup receipts. Private home prefixes redacted; no weights, credentials, private IPs or GPU UUIDs.
Archive SHA256: f90fe3afe7f4db7ec762d24573d2adb983a4a761021322b40e4effb9b1f8c776
Archive entries: 68
