Issue #24: v1.3.96 hot-helper promotion, PRO 5000 + PRO 4500

Upstream: v1.3.96 / 587bfb416ab230a83c84762adfb7264b7a6e9481.
Source addition: the same optional MXFP8 Engram reader patch used for
v1.3.94/v1.3.95, included in the archive. No local routing/helper changes.
Build options and engine/patch hashes are recorded in the archive.

Hardware: Ryzen 9 9900X, 192 GB RAM; primary RTX PRO 5000 72GB (physical
GPU1), helper RTX PRO 4500 32GB (physical GPU0). CUDA_VISIBLE_DEVICES=1,0.
Both links Gen5 x8. Driver and placement were checked on the machine.
Target: ISTA GSQ-RCO DeepSeek-V4.1-Flash-1017 IQ2_XS, Huihui attention-output
replacements, MXFP8 Engram; DSpark Q2K-Q4K draft. Unsplit target.

Common settings: helper cap 28 GiB (effective 27.865 GiB, 3096 residents),
12 CPU-lane threads, 128 decimal GB RAM budget, context 32768, chunk 4096,
16,384 input tokens / 2,048 output tokens, greedy / seed 42, DSpark enabled,
prompt reuse disabled. Exact environment and commands are in settings.json.
The four modes are helper OFF, helper ON with PROMOTE=0, PROMOTE=2, PROMOTE=4.

Two fixture families, each measured separately in fresh processes:
- original: the previously published warm-up, trial-01 and trial-02 inputs;
- identical: all three requests use the exact original trial-01 input IDs.
Each family/mode has two fresh processes, each with one discarded warm-up
and two measured requests: four measured requests from two processes.
Process order is reversed between A/B to reduce ordering effects. There
are 16 timed processes (48 requests, of which 32 are measured), followed by
two separate 16K/512 CHECK processes for PROMOTE=2 and PROMOTE=4.

analysis.json contains individual request metrics, measured medians/ranges,
first-4096-prefix speeds and whole-16384-token DONE prompt rates separately,
native STAT/glm stat records, helper-counter increments and diagnostics.
Native VRAM hit rate describes the primary VRAM tier, not combined helper hits.
prefill-events.txt extracts all PP/DONE, the final STAT, ds4 dspark, glm stat and helper
request_end lines for all timed processes, including discarded warm-ups.

complete-engine-logs.tar.xz includes COMPLETE stdout/stderr for all 18
processes, telemetry, protocol timelines, settings, fixtures and the harness.
No T, STAT, PP, READY or DONE lines are omitted from the complete streams.
The separate timelines omit T lines, which remain in full in engine.stdout.log.
Private home prefixes are redacted; no model weights, credentials, private
network addresses, GPU UUIDs or private host inventories are included.
log-manifest.json records hashes before/after redaction. The harness snapshot
has redacted machine paths; adapt those before running it on another host.

These are synthetic-workload measurements. Output token sequences can differ
between modes and repeat processes; there is no claim of identical output or
statistical significance. Numerical checks concern sampled RAM-tier expert
contributions and are not a full-model quality evaluation.

Archive bytes: 676532
Archive SHA256: 1e611b348318d267a06da5cd6cdad08178be1fe56b8e0fd05bd8ab2fcfcbe17c
Engine SHA256: 835c8670abec3b5d3e70faa3b240a1a93ef571d54b2038b50305d35a7eaa7870
Driver: 595.99.02; CUDA toolkit 13.0; Release build for sm_120a.
