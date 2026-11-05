# Issue35: paired v1.3.111 / v1.3.112 Qwen IQ3_S MTP comparison

Official v1.3.112 `c3d4e923b6df8027fc5a13aa2f6b22f6771e9150` versus v1.3.111 `5e8b9c44fec443fd1d0c9140885c47973f7970b4`, unpatched native CUDA13.0/sm_120a. Fresh version-paired measurements on both original PCs. This branch holds evidence; its inherited repository source is not the source used for these builds.

## Conditions and bounded results

Same Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S GGUF pair/native pack and RT MTP assets as the original report. Existing uniform gate/up pack reused unchanged; no UD-IQ1_S download, repack or weight conversion. Shipped prior file hash d62f4f0da4e8de44e05fdac38e9965855df12d64f6d21df29d05bdfc246ed721 verified equal across the versions. Same pinned GGML3cf03257f219afbe7334045ff7c6a06ac68c627d; four critical source Git-blob hashes freshly match the previously verified official commit, and the GeForce GGML checkout HEAD matches too.

* PRO system: Ryzen9 9900X,192GB RAM, physical0 PRO4500 32GB ->physical1 PRO5000 72GB, active Gen5x8 each, Samsung9100PRO2TB, Ubuntu24.04.5/kernel6.8.0-147-generic.
* GeForce system: i5-14400,128GB RAM, physical0 RTX5070Ti16GB Gen5x16 ->physical1 RTX5060Ti16GB Gen4x4, Samsung990PRO1TB, Ubuntu24.04.5/kernel7.0.0-42-generic.
* Driver595.99.02 on both. RAM budgets119.20928955GiB (128 decimalGB) /90GiB; context32768, greedy seed42, thinking off, prompt reuse off/asserted0, usage saving off. Default RT MTP K4/0.75 active, draft offers/accepts retained. No inference profiler, no optimization-disable override. Native engine argv/env and CPU calibration/placement are recorded for every process.
* PRO full single uses GPU1/chunkauto; native split22 uses GPU0,1/chunk2048. CPU lanes are inactive at full residency despite requested12. PRO cap single uses GPU1/32GiB/chunk4096/CPU12 shared; cap split20 uses GPU0,1/PARTS16,32/chunk4096/CPU6 per GPU, own pools (`CPU_SHARED=0`). GeForce single uses GPU0/chunkauto/CPU8 shared; dual uses GPU0,1/split32/chunk4096/CPU8 shared. The PRO caps are capacity-only budgets on unchanged PRO compute/bandwidth, not actual RTX5090/5070Ti performance.

| Setup | Prefill tok/s 111 ->112 | Decode tok/s 111 ->112 | Decode change | Wall median s 111 ->112 |
|---|---:|---:|---:|---:|
| PRO 5000 alone, native capacity | 3322 -> 3263 | 141.42 -> 144.34 | +2.07% | 19.498 -> 19.283 |
| PRO 4500 -> 5000, split22/chunk2048, native | 4373 -> 4376 | 131.48 -> 134.67 | +2.42% | 19.258 -> 18.879 |
| PRO 5000 alone, 32GiB budget | 2570 -> 2555 | 131.70 -> 134.01 | +1.75% | 21.975 -> 21.652 |
| PRO 4500(16) ->5000(32), split20/chunk4096 | 3985 -> 3980 | 128.47 -> 130.70 | +1.74% | 19.947 -> 19.758 |
| RTX 5070 Ti alone | 2073 -> 2078 | 56.07 -> 57.45 | +2.47% | 44.634 -> 43.301 |
| RTX 5070 Ti ->5060 Ti, split32/chunk4096 | 1973 -> 1959 | 77.32 -> 77.70 | +0.49% | 34.662 -> 34.638 |

Every row/version is one fresh process, one full16,384-input/2,048-output warmup and three measured original public prompts. Total12 accepted speed processes:36 measured plus12 warmup responses. Aggregate rates use total tokens/total respective DONE time; wall is native pipe-client latency. Exact per-request values, ranges and TTFT are in results.json. The next GEN is dispatched immediately after DONE; all accepted engines exit normally after final processing. Native split22 was included before measurements because it previously nearly tied the full single-GPU wall time; there was no outcome-based parameter search.

PRO order:111full,112full,112native-split22,111native-split22,111cap-single,112cap-single,112cap-split20,111cap-split20. GeForce order:111single,112single(retried after contamination),112split32,111split32. The previous valid111 single baseline was retained. One fresh start per row and three prompts do not establish statistical significance or a universal optimum; these are the gains observed on this model/workload, not a replication of the release's other models or4K/512 benchmark.

## Outputs, active graphs and separate numerical check

At native PRO capacity, both the single-GPU and split22 profiles match all2048 generated IDs exactly across versions for all four requests including warmup; draft accepted/offered counts also match. These are six measured prompt-pairs plus two warmup-pairs. The four partial-residency profiles have different continuations, sometimes from token0. Their route/calibration/MTP work can differ, so those session-rate ratios cannot isolate a kernel speedup. Full IDs, first-token IDs and first-difference positions are retained. This is a v111->v112 comparison; the earlier v109->v111 first-token question remains separate and under author investigation.

Default-on v112 graph use is confirmed by exit reports: about64.9-71.3% of reported layer segments replayed, with exact graph/capture counts per GPU. The GeForce split's second GPU reports44 re-captures; other tested reports show0. These are native graph counters, not a measurement of total CUDA launch-count reduction. No graph, fetch-column, wait-column or promotion ablation was added.

Separate from speed runs, the PRO full-resident single GPU scores the same16K prefix plus256 forced continuation IDs against the same published v109 top32+rest reference. The upstream protocol scores255 later continuation positions:

* quality-v111-full5000: `SCORE 255 tokens: nll 0.31308 ppl 1.3676 top1 98.43% | vs ref: KL 0.000956 (max 0.0139), same top token 98.43% | 0.5 ms/token (token path 10.55) | cpu lane 0 experts, vram hit 100.00%`
* quality-v112-full5000: `SCORE 255 tokens: nll 0.31308 ppl 1.3676 top1 98.43% | vs ref: KL 0.000956 (max 0.0139), same top token 98.43% | 0.5 ms/token (token path 10.54) | cpu lane 0 experts, vram hit 100.00%`

The rounded scores agree between111/112, with finite KL0.000956 to the old quantized reference. This does not measure direct pairwise-logit identity or independent full-precision model accuracy, nor does it settle the earlier109/111 question. It is a bounded forced-token consistency check; no arbitrary pass tolerance is imposed. Numerical timings are excluded from the speed table.

## One contaminated run, preserved and excluded

The initial v112 GeForce-single process detected independent `unattended-upgr` CPU use:2040ms over2.056s. All four requests' records are retained but the entire process is excluded from primary metrics. The legacy protocol loop observed the audit failure at the end despite sending TERM; no part of that run is reused as a timing sample. Event/dispatch-level audit checks were tightened for the retry so an audit failure immediately stops dispatch and terminates only our engine (TERM, then KILL after20s if necessary). Native engine code/arguments and timing settings were unchanged. The initial and checked harness versions are both retained.

The two GPU services were restored after that failure. The OS updater was not stopped or reconfigured. System unit readback showed the upgrade jobs inactive before the retry and quiet preflight passed. Apt logs record upgrades only to apt/apt-utils/libapt and python3-twisted in this window, completed06:36:38UTC; the running kernel and NVIDIA driver stayed the same. The clean retry contains a new full warmup plus all three measured requests. Other uncontended processes were not repeated. Both the excluded records and update log tails/classification are included.

## Resource and preservation proof

Each host holds its shared GPU lock through its local build/measurement/diagnostic sequence. The two machines read separate local SSDs and do not share model storage or compute. All-readable-process CPU/IO/RSS, global NVMe, GPU and memory audits start with quiet preflight before load/calibration and continue through exit. The PRO numerical check follows all PRO speed runs on its independent resources; GeForce timing may still be running on the other host. No contention or thermal/resource trip occurred in accepted processes. Sampled maxima:{"NVIDIA RTX PRO 4500 Blackwell": 75.0, "NVIDIA RTX PRO 5000 72GB Blackwell": 86.0, "NVIDIA GeForce RTX 5070 Ti": 65.0, "NVIDIA GeForce RTX 5060 Ti": 65.0} (limits PRO4500/GeForce85C,PRO5000 90C). Sampling cannot exclude all brief OS events or inaccessible process details.

Both previously active GeForce GPU services were confirmed with empty queues and idle GPU/CPU, temporarily stopped, restored on failure and final success, then checked active with their GPU reservations. Cached model residency in those services is runtime state, not a preserved memory-size setting. No PRO service was changed. Final proofs show own GPU engines gone and both locks free, clean pinned sources and unchanged built/control binary hashes, original model/pack/MTP sizes and modification times unchanged, metadata hashes retained. Full weight hashing was not run during timing; previous full GGUF hashes remain in the v109 evidence. Common configs, model originals, power/clock/fan policy and other processes were not changed.

* dual-pro-system: v111 SHA256 `c42db7715630787d31bbc9a22cf92cf117c6264d0644b5608d4e692882c9e7b0`, v112 SHA256 `be22c4f747af1efc37ad9e8c0317fd9b54a053bc4ce18dd6540588b50071d7a5`
* geforce-system: v111 SHA256 `261fd3e975e28533af574170dc4177ca2547b6ab8e809101406bb5f676421422`, v112 SHA256 `ef693bfcff5461969d8704b071c353187d478da85ab690ac39a0a47e240a009c`

The archive contains unabridged T/PP/STAT/INFO/READY/DONE/glm stat and graph reports, all inputs/output IDs and first-difference data, per-case settings, host/GPU telemetry, source pins/build commands/logs/hashes, forced-score reference and logs, excluded attempt plus guard-change and OS-update evidence, and cleanup/service proofs. Paths, private identifiers and credentials are redacted; no model weights. Per-entry SHA256 manifests and exact published readback are required before the Issue reply.
