Abyss Issue #24: v1.3.101 immediate-next-request interruption smoke

Pinned release: v1.3.101 / f6380df9d614f5ce8e11c446ff76c28a3834f0e6
Engine SHA256: 35ea6bec3b722f8ed5f7a3d319d4ddb32852da7c60c2371a1f3665510d530e57
Author request: https://github.com/zephel01/Abyss/issues/24#issuecomment-6590781302

Same unsplit ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention replacements + MXFP8 Engram, DSpark Q2K-Q4K enabled. PRO 5000 72GB primary / PRO 4500 32GB helper, PCIe Gen5 x8 each; CUDA_VISIBLE_DEVICES=1,0. Helper cap 28 GiB, PROMOTE=0, CPU lane 12, RAM budget 128 decimal GB, context 32768, chunk 4096, greedy/seed 42, prompt reuse disabled. Same optional MXFP8 reader adapter as prior tests (SHA256 c2c26136fe086b4a1641e4c70878baa0eb8508fa2bbebc835cad54b3e76390ff); no local helper/resync changes. Only RESYNC differs within this test.

One fresh process for each mode, three requests per process: one discarded warm-up followed by two observed next-request transitions, six 16K/512 requests in total. All use the exact original trial-01 input IDs (SHA256 13f9df432a5568ac5ea8aed610a9949e27414abf94ad73b414181bf8a1e8de1a). The next pre-encoded GEN is sent immediately after DONE, before parsing or saving metrics. Timers start before stdin write/flush; the between-request wait is included. The final resync completes before QUIT, under continued resource monitoring.

| RESYNC | Next request | Previous resync promotions / ms | GEN gap after DONE ms | Client wall minus native prompt+Decode ms |
|---:|---|---:|---:|---:|
| 0 | trial-01 | none | 0.102 | 0.669 |
| 0 | trial-02 | none | 0.127 | 0.651 |
| 8192 | trial-01 | 16 / 7.5 | 0.078 | 8.052 |
| 8192 | trial-02 | 16 / 6.1 | 0.076 | 6.628 |

Enabled resync logs (the final line is deliberately drained before shutdown):
expert helper resync: 16 promotions in 7.5 ms (stopped: the next request)
expert helper resync: 16 promotions in 6.1 ms (stopped: the next request)
expert helper resync: 826 promotions in 539.5 ms

Prior v1.3.99 smoke: 120 promotions per interrupted round, 42.9 / 41.8 ms; next-response wall-minus-native 43.201 / 42.163 ms. Prior no-resync control: 0.592 / 0.726 ms.

First-prompt whole-16K Prefill, RESYNC 0 / 8192: 2677.0 / 2716.5 tok/s. Startup glm fast / glm prefill tier and warm-up lines are included in prefill-events.txt and unabridged stderr. No dedicated startup-slow rerun.

Peak helper / primary temperatures: 44 / 73 C. No thermal-slowdown flags, helper fallbacks, resync errors or resource-guard trips. Pack metadata hashes, model sizes/mtimes and running user services unchanged; engine processes exited. Preservation does not hash every model weight.

This is the requested interruption smoke, not a repeat of the 16K/2K performance comparison or a full-model accuracy test. There are only two transitions per mode from one process; no new numerical CHECK run. Output IDs vary. The v1.3.99 data below were collected earlier, not in a simultaneous randomized version A/B.

The archive contains unabridged stdout/stderr (all T/STAT/PP/READY/DONE records), both reader timelines, request metrics and output IDs, telemetry, exact input fixtures/settings, before/after preservation receipts, build commands/log/options and source/adapter hashes, the harness and author request. Timelines omit T lines only; stdout is complete. Private home prefixes are redacted; no model weights, credentials, private IPs or GPU UUIDs are included. The raw local archive remains private.

Whole-16K Prefill uses 16384*1000/DONE prompt_ms; first PP covers only the first 4K. The final STAT before each DONE is checked against native Decode timing and glm stat. Helper request_end counters are cumulative per process. Client wall minus native time includes native post-DONE resync waiting plus client/IPC overhead; the no-resync control measures that baseline. This does not measure an exact individual-copy latency.

Public archive SHA256: 2e8930e2fba713ad067c6b02cc926e97e17724eb1771123484c545e6a6c4f984
Archive entries: 37
