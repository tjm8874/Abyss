Abyss Issue #24: v1.3.102 interruption smoke

Pinned commit: e4eaf01f089a3e7fb2621720fac17e5cb241c223
Engine SHA256: 42ac81a4724fe30b7e6bc08b5d5b44c0c1025d5cb5d28ee5302f11a6380422d0
Author request: https://github.com/zephel01/Abyss/issues/24#issuecomment-6593133530

| Input timing | RESYNC | Next request | Previous resync promotions | Resync ms | Logged longest gap ms | GEN gap after DONE ms | Client wall minus native ms |
|---|---:|---|---:|---:|---:|---:|---:|
| immediate | 0 | trial-01 | none | — | — | 0.078 | 0.715 |
| immediate | 0 | trial-02 | none | — | — | 0.077 | 0.554 |
| immediate | 8192 | trial-01 | 1 | 0.5 | 0.44 | 0.073 | 0.935 |
| immediate | 8192 | trial-02 | 0 | 0.2 | 0.11 | 0.076 | 0.711 |

back-to-back-r8192
expert helper resync: 1 promotions in 0.5 ms (stopped: the next request) (longest gap between next-request checks 0.44 ms)
expert helper resync: 0 promotions in 0.2 ms (stopped: the next request) (longest gap between next-request checks 0.11 ms)
expert helper resync: 736 promotions in 502.4 ms (longest gap between next-request checks 1.21 ms)

Two primary fresh processes, one per RESYNC mode, with three identical 16K/512 requests each: one discarded warm-up and two next-request transitions. The declared zero-promotion trigger did not fire, so no delayed-input probe was added. Total: 2 processes, 6 requests. The next pre-encoded GEN is sent before parsing/saving metrics. Request timers start before stdin write/flush; the intentional 2 ms gap, when present, is excluded. Timers include any post-DONE work still pending after the next send. Every final post-DONE resync drains before QUIT under continued monitoring.

Same unsplit ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention replacements + MXFP8 Engram; DSpark Q2K-Q4K enabled. PRO 5000 72GB primary + PRO 4500 32GB helper, Gen5 x8 each; CUDA_VISIBLE_DEVICES=1,0, helper cap 28 GiB, PROMOTE=0, CPU lane 12, RAM budget 128 decimal GB, context 32768, chunk 4096, greedy/seed 42, reuse disabled. Exact original trial-01 input IDs for every request (SHA256 13f9df432a5568ac5ea8aed610a9949e27414abf94ad73b414181bf8a1e8de1a). Same optional MXFP8 reader adapter (SHA256 c2c26136fe086b4a1641e4c70878baa0eb8508fa2bbebc835cad54b3e76390ff); no local helper/resync changes. Only RESYNC differs within the immediate pair.

Earlier same-smoke results: v1.3.99 interrupted after 120 promotions in 42.9/41.8 ms, client residual 43.201/42.163 ms (control 0.592/0.726); v1.3.101 after 16 promotions in 7.5/6.1 ms, residual 8.052/6.628 ms (control 0.669/0.651). Historical summaries are retained in analysis.json.

**The startup-slow case recurred in the RESYNC=0 process.** It was slow before any resync and stayed slow for its next two prompts. All runs are retained; there was no dedicated startup rerun. The enabled process was already faster on its very first prompt, so the cross-mode Prefill difference here cannot be attributed to RESYNC.

| Current process | First prompt, before any resync tok/s | Next two whole-16K prompts tok/s | THP at last RAM-tier registration GB |
|---|---:|---|---:|
| back-to-back-r0 | 2047.4 | 2074.5 / 2094.7 | 8.6 |
| back-to-back-r8192 | 2705.2 | 2736.8 / 2749.0 | 12.1 |

Both current starts report identical VRAM-before-pool usage (7.82 of 71.12 GB, dense 5.24 / state-KV 0.00 / activations 0.09 / other 2.49) and RAM tier (83.87 GB pinned, 9272 slots). The THP totals differ, but they do not identify a cause: the saved v1.3.99 startup-slow A and normal B processes had 73.2 and 73.5 GB in THP at the last registration, respectively, despite first-prompt rates 2045.3 and 2707.1 tok/s. Current and historical per-mmap MADV_HUGEPAGE/free-block lines and all glm fast / glm prefill records are included. Placement remains an observation to investigate, not a confirmed explanation.

All helper request_end lines have fallbacks 0. No resync errors, thermal-slowdown flags or resource-guard trips. Peak helper/primary temperatures: 44/75 C. Pack metadata hashes, model sizes/mtimes and running user services unchanged; processes exited and lock free. Preservation does not hash every model weight.

This is a bounded interruption check, not a new repeated 16K/2K throughput comparison or a full-model accuracy test. Only two transitions are observed per fresh process; output IDs vary. No new numerical CHECK run. Historical v1.3.99/v1.3.101 results were collected earlier, not in a simultaneous randomized version A/B. The engine longest-gap field measures intervals between server-side checks; client wall minus native prompt+Decode also includes IPC/client overhead and any waiting outside the native timers. These are different measurements, not interchangeable latency guarantees.

Whole-16K Prefill uses 16384*1000/DONE prompt_ms; first PP covers the first 4K only. Final STAT before each DONE is checked against native Decode timing and glm stat. Helper counters are cumulative per process.

The archive contains unabridged stdout/stderr (all T/STAT/PP/READY/DONE lines), both reader timelines, telemetry, request metrics/output IDs, exact inputs/settings, harness, build commands/log/options and source/adapter hashes, before/after preservation receipts, author request and the predeclared extension policy/decision. Timelines omit T lines only; stdout is complete. Private home prefixes are redacted; no model weights, credentials, private IPs or GPU UUIDs are included.

Archive SHA256: 264c508b8fa2b976b09f50c2b23e5b631268cd98e6762039245529c77124e527
Archive entries: 40
