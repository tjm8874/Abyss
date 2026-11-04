# Issue35: v1.3.111 targeted loading and long-MTP follow-up

Pinned official **v1.3.111 /5e8b9c44fec443fd1d0c9140885c47973f7970b4**, unpatched native CUDA 13.0/sm_120a, driver 595.99.02. Binary SHA256 `261fd3e975e28533af574170dc4177ca2547b6ab8e809101406bb5f676421422`. Includes v1.3.110's fixes from51ef4059389cb5a0f5af91c7ff353e4271634f78. GGML remains pinned3cf03257f219afbe7334045ff7c6a06ac68c627d. The inherited repository source on this evidence branch was not the source used for the measured build.

Actual hardware: i5-14400,128 GB RAM; physical 0 RTX5070 Ti16GB on activeGen5 x16 and physical 1 RTX5060 Ti16GB on activeGen4 x4. Ubuntu24.04.5/Linux7.0.0-42-generic, local Samsung 990 PRO 1TB model storage. Same Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S GGUF pair/native pack/RT MTP assets as the original v1.3.109 report. RAM 90 GiB,context 32768,CPU 8 shared, shipped expert-count prior, greedy seed 42, thinking off,reuse disabled and asserted0. Next GEN follows DONE immediately; valid cases quit normally and complete exit processing. Exact input/output IDs, complete logs and guards are in the archive.

## Two reported loading fixes

* **Manual split46 now works on two actual GPUs.** Physical0 owns[0,46),physical 1 owns[46,48); the MTP drafter is on the last card. One 2K/64-token warmup,one 2K/256 andone 16K/128 request completed, versus the v1.3.109 startup rejection. This is a targeted loading/decode check, not a new optimum for split position.
* **The kept card now uses its own VRAM cap.** With physical order5060 Ti ->5070 Ti (`CUDA_VISIBLE_DEVICES=1,0`) and `STRATA_GLM_VRAM_GB_PARTS=3,14`,auto predicts logical CUDA1 alone17.1 ms versus17.6 ms for its best split, keeps that card, and logs `CUDA1 VRAM cap 14.0 GB`. It loads[0,48) and completes2K/64 plus2K/256 requests with MTP. This directly exercises the second-entry cap mapping on distinct cards. The original PRO16,32 case was not rerun; its original measurements remain pinnedv1.3.109.

The normal5070->5060 order with3,14 selected a valid split5, so it did not cover one-card fallback. Its two completed2K requests are retained; the irrelevant, very slow in-flight16K probe was intentionally stopped (TERM thenKILL of only our exact engine process), with no rate assigned to that incomplete request. A subsequent1,14 probe was below the first card's startup floor and was refused; also retained without a speed result. Reversing the valid3,14 order then exercised the intended branch. These diagnostics are separate from the table below.

## Fixed16K/2K comparison

| v1.3.111,16K input /2K output | Prefill tok/s | Decode tok/s | Wall median [range],s | n |
|---|---:|---:|---|---:|
| 5070 Ti alone, chunk auto | 2067.3 | 54.68 | 45.509 [45.108,45.535] | 3 |
| 5070 Ti ->5060 Ti,split 32,chunk 4096 | 1967.9 | 76.86 | 34.757 [34.722,35.442] | 3 |

Each row has one fresh process, one full16K/2048 warmup and the same three measured public prompts asv1.3.109. Rates are total tokens/total native time; wall uses the pipe client. The split reduces median wall by23.6% in this sample. Priorv1.3.109 was56.25/78.54 decode tok/s and43.984/34.176s wall for single/split. All three measured continuations in each configuration differed from v1.3.109; several first mismatches occurred at token 0. Separate sessions, calibration and different greedy continuations can change routing/MTP work; these small samples do not establish a release-level speed change. Full per-request values and v1.3.109 output-hash comparisons are in results.json. No auto-cost-model refit is claimed; hand split 32 remains the measured configuration.

## Long-input MTP scratch path

Single5070 Ti,explicit `--prefill 32768`,context 32768,RT MTP active. One separate2K/64 warmup then one request at each length,512 generated IDs each. The stress inputs prefix8K/12K IDs from the original16K fixture to that complete fixture, preserving its final instruction; their exact lists and hashes are included. PP confirms actual batches above20K, and both requests finish without invalid-expert/non-finite-router errors.

| Input IDs | Largest observed main PP batch | Generated IDs | Draft accepted/offered | Prefill tok/s | Decode tok/s |
|---:|---:|---:|---:|---:|---:|
| 24576 | 24575 | 512 | 260/317 | 2125.2 | 56.03 |
| 28672 | 28671 | 512 | 245/309 | 2109.2 | 55.91 |

These are bounded correctness smoke tests on IQ3_S. No Swift IQ2_XS model was substituted; no cross-version bitwise identity, full-precision accuracy or general task-quality claim is made. Long-input timings are excluded from the16K table.

## Preservation, safety and scope

The shared GPU lock and all-readable-process CPU/IO/RSS audit cover quiet preflight through each engine exit. Two-second GPU/temperature/RAM/swap guards stop only our engine. No independent heavy-work or resource-guard event was detected. Sampled maximum temperatures: {"NVIDIA GeForce RTX 5070 Ti": 67.0, "NVIDIA GeForce RTX 5060 Ti": 67.0}; both limits85 C. The explicit diagnostic stop above is distinct from a guard trip or crash.

The two previously active GPU user services were confirmed idle, temporarily stopped under the lock and restored in every success/failure path. Final readback confirms active services and their GPU processes, no own GPU process, and a free shared lock. Source remains clean and the final binary matches its build hash. Original model/pack/MTP sizes and modification times match before/after; small metadata hashes are included. The earlier full weight hashes are in the v1.3.109 evidence; this follow-up did not repeat heavy weight hashing during measurement. No common configuration, original model, power/clock/fan setting was changed.

The PRO host was occupied by an independent benchmark, which was neither stopped nor messaged. Its previous optimization/capacity data remainsv1.3.109; this follow-up's generic loading and long-prompt paths were verified on the real GeForce pair. It does not add new PRO or virtualRTX5090 performance claims. Numerical quality/stock-deep-bench results fromv1.3.109 remain separate.

All completed and failed/stopped probes are retained. Archive has complete T/PP/STAT/INFO/READY/DONE/glm stat lines, output IDs, host and GPU audits, fixed/corrected-before-use long-input fixtures, settings, build commands/log/provenance, reviewed upstream patches, intentional-stop record, preservation and service restoration proofs. Private paths/process IDs are redacted; no model weights. Per-entry SHA256 manifests and exact GitHub readback accompany publication.
