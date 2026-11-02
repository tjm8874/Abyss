Issue #24: v1.3.99 interactive helper resync 0 / 8192

Upstream: v1.3.99 / 37833d59eb7c130ecd5b5c3abde509bd4744f34a.
The only local engine addition is the previously published optional MXFP8
Engram reader patch. No helper, resync or cancellation code is modified.
Build options, patch and engine hash are included.

Primary RTX PRO 5000 72GB (physical GPU1), helper RTX PRO 4500 32GB (physical
GPU0), both Gen5 x8 when active. CUDA_VISIBLE_DEVICES=1,0. Ryzen 9 9900X,
192 GB RAM; driver 595.99.02, CUDA toolkit 13.0, Release / sm_120a.
Same unsplit ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention
output replacements + MXFP8 Engram, with the DSpark Q2K-Q4K drafter.

Both primary modes: helper ON, PROMOTE=0, cap 28 GiB (effective 27.865 GiB),
CPU lane 12, RAM budget 128 decimal GB, context 32768, chunk 4096, greedy /
seed 42, prompt reuse OFF. Only RESYNC=0 versus 8192 differs between modes.

Interactive comparison: exactly five seconds are scheduled from receipt of
each DONE to the next request send, in BOTH modes. Request wall/TTFT timers
start before writing/flushing that next GEN; the intentional gap is excluded.
Observed gaps and native prompt/Decode timings remain in the JSON. Process
measured_pair_span_s includes two idle gaps; measured_response_wall_sum_s
excludes them. These are deliberately different metrics.

Two fixture families are separate: original public warm-up/trial-01/trial-02,
and identical-input (all three use original trial-01 IDs). Each family/mode
initially has two fresh processes, each with one discarded 16K/2K warm-up and
two measured 16K/2K requests. A/B order is reversed. A pre-resync first warm-up
below 2500 tok/s triggers one bounded matched process-pair repeat for that
family; extension-policy.json records the rule and when it was declared.
Every original process remains in overall medians, and startup-slow cases
are explicitly flagged. Actual counts are given in the verified footer.

Separate interruption smoke: helper ON / PROMOTE=0, RESYNC=0 and 8192,
three identical 16K/512 requests per fresh process, sent immediately after
DONE. These two processes test cancellation timing and are excluded from the
primary speed comparison. Their settings, rows and logs are preserved.

Separate numerical check: RESYNC=8192, two identical 16K/512 CHECK requests,
with the same five-second gap. The second follows the first resync. This
single process is excluded from speed comparisons. Final cumulative reference
metrics cover sampled RAM-tier expert contributions, not full-model quality
or every promoted VRAM computation. Actual total log counts are in the footer.

Final resync handling: the harness waits for the final completion log before
sending QUIT, so shutdown does not cancel final work. Every resync records
promotion count, duration, completion time and whether the next request
stopped it. For each primary transition the JSON records whether the preceding
resync had completed before the next send. A five-second pause is a fixed
workload condition, not an assumption that catch-up always finishes within it.

analysis.json contains individual rows, native final STAT/glm stat, medians /
ranges, helper-counter increments, resync records, process summaries and smoke
results. Whole-16K Prefill is derived from native DONE prompt_ms; the first
4096-token prefix rate is separate. Native VRAM hit is primary Decode VRAM
hit, not combined helper hits. Decode promotions/token exclude post-DONE
resync promotions. prefill-events.txt associates each timed request's PP,
final STAT, DONE, glm stat, DSpark and helper records with its resync record.

complete-engine-logs.tar.xz includes COMPLETE stdout/stderr from all 11
processes, stdout/stderr reader timelines, telemetry, exact inputs/settings,
harness, patch and build provenance. All T/STAT/PP/READY/DONE lines are retained
in engine.stdout.log; the separate protocol timeline omits T lines. Private
home prefixes are redacted, and no weights, credentials, private network
addresses, GPU UUIDs or private host inventories are included. Manifest hashes
identify originals and published bytes. Redacted harness paths need adapting
before reuse on another machine.

This is a synthetic workload. Output IDs may differ between modes and repeat
processes, and there is no identical-output or statistical-significance claim.
Native request_end counters are cumulative per process; request increments
are provided separately.

Verified final counts: 10 primary processes, 20 measured requests, 10 discarded warm-ups.
Total: 13 engine processes and 38 requests including smoke/check runs.
Original family: three fresh processes per mode, six measured requests per mode.
Identical family: two fresh processes per mode, four measured requests per mode.
All original data, including original-r8192-A, is retained in aggregate medians.
Archive bytes: 460836
Archive SHA256: 88f632ff06e249e00549f57820965479762fe0f3968a70e5423a651ee93b027a
Engine SHA256: 960c475ba84179867a1596a7ececc4b7ffd440ab9ada5da5b90ee2cc532d6e99
