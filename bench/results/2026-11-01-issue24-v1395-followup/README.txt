Issue #24: PRO 5000 + PRO 4500, v1.3.95 follow-up

Engine: v1.3.95 / e8d4847063018769cea1ea2ff9ba59f4966f42a4
Engine SHA256: e47c943e7f57db9c6acf1576c02e9bc1cc580ecc3e50815e515c110741f15842
Source addition: previously published MXFP8 Engram reader only.

complete-engine-logs.tar.xz contains COMPLETE engine stdout and stderr streams.
No T, STAT, PP, READY or DONE lines are omitted from those streams. Private
home-directory prefixes are replaced by <HOME>/<LOCAL_HOME>. The manifest
records the original and published hashes, and the archive contains no model
weights, credentials, addresses, or private host inventories.

v1.3.95: four timed processes, off-A/on-A/on-B/off-B; one 16K/2K warm-up and
two measured 16K/2K requests per process. Two separate 16K/512 diagnostic
processes use STRATA_GLM_EXPERT_HELPER_CHECK=1 and are excluded from timings.
The protocol timeline retains all stdout lines except T lines, which are
available in full in engine.stdout.log. Each request is identified by order:
warmup-01, trial-01, trial-02. Request JSON contains the input/output hashes,
native DONE timings, PP lines and memory snapshots.

v1.3.94: all four previous timed processes, including the original slow on-A
and faster on-B, are provided separately for the original Prefill question.

prefill-events.txt is a convenience extraction of ALL PP/DONE, ds4 dspark,
glm stat and helper request_end records for the timed processes of BOTH
versions. Complete unfiltered streams are in the archive.

GPU mapping: CUDA_VISIBLE_DEVICES=1,0; logical CUDA0 = PRO 5000 72GB,
logical CUDA1 = PRO 4500 32GB. Both links Gen5 x8. Target unsplit; helper cap
28 GiB; DSpark ON; context 32768; chunk 4096; 12 CPU lane threads; RAM budget
128 decimal GB; greedy, seed 42, thinking OFF, no prompt reuse. The same
published synthetic fixture token IDs are used in all cases.

The harness snapshot is provided for audit, with machine-specific home paths
redacted. Adapt those paths before reuse; the benchmark engine is the
upstream release commit named above. This branch stores evidence only.

Archive SHA256: d49142eaa9b5cd5e99c362d4dc91b882afd3085c90ba0b0b711c310016a1ca12
Archive bytes: 288564
