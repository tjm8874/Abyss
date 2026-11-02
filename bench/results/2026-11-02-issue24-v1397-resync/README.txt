Issue #24: v1.3.97 post-DONE helper resync, PRO 5000 + PRO 4500

Upstream v1.3.97 / f2b93689b1ea5efa13eb569778cd09a25ae35c9e.
Source addition: the same optional MXFP8 Engram reader used in previous
measurements; no local routing/helper/resync changes. Patch, build options
and engine hashes are included in the archive.

Primary RTX PRO 5000 72GB (physical GPU1), helper RTX PRO 4500 32GB (physical
GPU0); CUDA_VISIBLE_DEVICES=1,0. Both active links Gen5 x8. Ryzen 9 9900X,
192 GB RAM, driver 595.99.02, CUDA toolkit 13.0, Release build for sm_120a.
Same ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS + Huihui attention-output
replacements + MXFP8 Engram; unsplit target and DSpark Q2K-Q4K draft.

All modes: helper ON, PROMOTE=0. RESYNC=0, 96 or 192 is the only environment
difference. Cap 28 GiB (effective 27.865 GiB), CPU lane 12, RAM budget 128
decimal GB, context 32768, chunk 4096, greedy / seed 42, prompt reuse OFF.

Two fixture families:
- original: previously published warm-up, trial-01, trial-02 input IDs;
- identical: all three requests use the exact original trial-01 input IDs.
Each family/mode has two fresh processes, each with one discarded 16K/2K
warm-up and two measured 16K/2K requests. Four measured requests come from
two processes, not four independent process replicates. A/B order reversed.
12 timed processes: 36 requests, including 24 measured and 12 warm-ups.
Two separate CHECK processes (96 and 192) each run two 16K/512 requests,
so the second numerical check runs after a resync. Checks are excluded from
all speed comparisons. The final post-DONE resync is drained before exit.

Back-to-back timing: after reading DONE, the harness dispatches the next
pre-encoded GEN immediately, before parsing/saving metrics or other I/O.
The request timer starts before stdin.write/flush. Any resync wait is
therefore included even if the input write blocks. Reader-thread timestamps
record T/DONE arrival independently. There is no intentional inter-request
pause. Send times, dispatch duration, client gaps, whole-prompt/native Decode
times, request wall time and wall-minus-native residual are preserved.

RESYNC runs after DONE and is excluded from that response's native prompt/
Decode timers. For a continuous stream, it is paid by the next response.
Measured trial-01 waits for the warm-up's resync; trial-02 waits for trial-01's.
The final resync is also logged/drained but is not counted twice in response
wall time. following_resync_ms identifies the work after the given response;
preceding_resync_ms identifies work whose wait can affect that response.
Decode promotions/token and post-DONE resync promotions are separate metrics.

analysis.json includes native final STAT/glm stat records, individual metrics,
medians/ranges, helper-counter increments and resync counts/times. Whole-16K
Prefill is derived from native DONE prompt_ms; first-4096-prefix rates are
separate. Native VRAM hit is the primary's Decode VRAM tier hit, not a combined
helper hit rate. prefill-events.txt extracts all PP/DONE, final STAT, glm stat,
ds4 dspark, request_end and associated post-DONE resync records.

complete-engine-logs.tar.xz includes COMPLETE stdout/stderr for all 14
processes, both reader timelines, telemetry, settings, exact input IDs,
harness, adapter patch and build provenance. All T/STAT/PP/READY/DONE lines
remain in engine.stdout.log; the separate protocol timeline omits T lines.
Private home prefixes are redacted. No weights, credentials, private network
addresses, GPU UUIDs or private host inventories are included. Manifest hashes
identify original and published data. Redacted harness paths require adapting
before reuse on another machine.

These are synthetic-workload measurements. Generated token IDs may differ
across modes and repeat processes; no identical-output or significance claim.
Numerical checks concern sampled RAM-tier expert contributions, not complete
model quality. Native request_end counters are cumulative within each process;
per-request increments are provided separately.

Archive bytes: 519404
Archive SHA256: a14f98509c28a2511b5c419c151fae200bd48320b67ce812b2a74f32093dbce0
Engine SHA256: 39814e86f02ed0c6ec55a7d5593b2b57c299552eac2ebef722837dceba70ed8e
