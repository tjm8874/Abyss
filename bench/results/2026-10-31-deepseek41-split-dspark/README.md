# DeepSeek V4.1 layer splitting with a tail-local DSpark drafter

Experimental patches for Abyss **v1.3.88 / `93ac6000e036f6f98b46089ba7a40dec95b69839`**. This was the upstream `main` head when prepared on 2026-10-31. Related: [issue #21](https://github.com/zephel01/Abyss/issues/21) and the merged [expert-helper PR #22](https://github.com/zephel01/Abyss/pull/22). This is a different path: layer ownership plus speculative verification, rather than a Decode-only expert helper.

## Files and application

1. `0001-deepseek41-layer-split-dspark.patch`: layer-boundary validation, Prefill state handoff and prompt-skip propagation, split Verify state/Engram handling, and a DSpark drafter on the final part. Includes the four diagnostic switches in the repository's debug-setting list. It does **not** depend on the separate MXFP8 adapter.
2. `0002-optional-mxfp8-engram-adapter.patch`: only needed for the MXFP8 Engram pack used in these measurements. Includes the previously external `engram_mxfp8.hpp` dependency. Other upstream-supported Engram formats do not need this patch.
3. `benchmark_native.py` and `benchmark-fixtures.json.gz`: standalone native-protocol speed replay, using only Python's standard library. The three fixture inputs are fictional warehouse inventory/code-generation requests, already tokenized with the measured model's tokenizer and thinking OFF suffix. Each has 16,384 tokens. No model weights are included.
4. `benchmark-results.json`, `quality-summary.json`, `engine-log-excerpt.txt`: measurements and selected evidence. These are existing measurements, not new results from the packaging validation build.

From a clean checkout of the base commit, with these patch files available:

```sh
git apply --check /path/to/0001-deepseek41-layer-split-dspark.patch
git apply /path/to/0001-deepseek41-layer-split-dspark.patch
# Optional, for a prepared MXFP8 Engram pack only:
git apply --check /path/to/0002-optional-mxfp8-engram-adapter.patch
git apply /path/to/0002-optional-mxfp8-engram-adapter.patch
```

Build with the repository's normal CUDA instructions. The validation build used Release, CUDA 13.0, `sm_120a`, and:

```sh
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DSTRATA_ENABLE_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120a \
  -DSTRATA_BUILD_TESTS=OFF -DSTRATA_GGML_DIR=/path/to/llama.cpp
cmake --build build --target strata -j 4
```

The feature patch and optional adapter reconstruct the measured six C++/CUDA files and MXFP8 header byte-for-byte. The only packaging addition is the debug-setting list. Measured engine SHA256: `1f66fc086a6f8666cfcb17fb9317dd8872285e708dbcee8c3e867afda8450cbc`. A fresh build's binary hash need not match because build paths/environment can differ.

## Reproduce the four configurations

Prepare an existing compatible native V4.1 pack and obtain the matching V4.1 DSpark drafter (`deepseek41-dflash-draft`; the measured file was Lucebox's `DeepSeek-V4.1-Flash-1017-DSpark-draft-Q2K-Q4K.gguf`, 4,923,041,440 bytes). Model packing, model-weight edits, and downloads are not performed by this replay script. Use the same prepared pack for every mode.

Run only when the selected GPUs are available. The script does not stop any services. On the measured desktop, physical GPU 0 was PRO 4500 and GPU 1 was PRO 5000. Override `--devices` for another ordering. For example:

```sh
python3 benchmark_native.py --engine /path/to/build/strata \
  --pack /path/to/v41-pack --mode split-on --devices 0,1 \
  --drafter /path/to/v41-dspark.gguf --out results-split-on
```

Run a fresh process for each mode, using a distinct output directory:

| Mode | Devices on this desktop | Draft file |
|---|---|---|
| `single-off` | `1` | not used |
| `split-off` | `0,1` | not used |
| `single-on` | `1` | required |
| `split-on` | `0,1` | required |

Split mode sets `STRATA_GLM_SPLIT=8`, with PRO 4500 owning layers 0–7 and PRO 5000 layers 8–39 plus the head. The drafter captures layers 36–38 locally on the final part. Expert helper is unset. Existing defaults for confidence threshold, maximum five drafts, and n-gram assistance are retained.

Both ON and OFF retain `STRATA_GLM_NO_SPEC=1`, matching the measurements: this disables the separate NextN/pipelined mechanism, not the explicit DSpark Verify path. ON sets `STRATA_DS4_SPEC=1`, `STRATA_DS4_DSPARK`, engine `--spec 5`, and **request `spec=1`**. OFF sets `STRATA_DS4_SPEC=0`, engine `--spec 0`, request `spec=0`. The earlier harness hard-coded request `spec=0`; changing only the startup arguments would not activate DSpark.

The replay discards one full 16K/2K warm-up and measures two requests, verifies actual input/output lengths and zero reuse, and records draft acceptance. It does not grade answer quality. Engine Prefill/Decode use the native `DONE` timings; TTFT/wall time are observed by the client. Model load time is excluded.

## Measurements

Ryzen 9 9900X; DDR5 192 GB; Linux; PRO 5000 Blackwell 72 GB plus PRO 4500 Blackwell 32 GB, each wired x8; CUDA 13.0 / driver 595.99.02. Native pack: ISTA GSQ-RCO DeepSeek V4.1 Flash 1017 **IQ2_XS**, Huihui attention-output replacement, **MXFP8 Engram**. Context 32,768; chunk 4,096; CPU lane 12 threads; RAM-tier budget 128 decimal GB (`119.20928955078125` GiB). Greedy, seed 42, thinking OFF, prompt reuse zero, lossy expert skips OFF, concurrency one. The existing lossless prompt-skip path remains enabled.

All rows below use one warm-up plus two measured requests, without the separate quality checks preceding them. The corresponding inputs have identical token-ID hashes. They are custom Python-generation measurements, **not the standard `--bench` suite**, and use different local builds of the same upstream release.

| Configuration | Run | Prefill tok/s | Decode tok/s | TTFT s | Wall s |
|---|---|---:|---:|---:|---:|
| PRO 5000, no DSpark | M_SINGLE | 2937.4 | 70.42 | 5.579 | 34.661 |
| split=8, no DSpark | M_W8 | 3747.7 | 72.49 | 4.373 | 32.628 |
| PRO 5000 + DSpark | W_S1dd | 2929.3 | 92.03 | 5.595 | 27.852 |
| split=8 + DSpark | W_SP8dd | 3749.8 | 92.93 | 4.372 | 26.445 |

For split=8 + DSpark, measured Decode was 89.18 and 96.68 tok/s; draft acceptance was 87.2% and 90.0%. The final part's drafter uses 1.67 GB VRAM, reducing its target expert pool from 219 to 213 slots/layer.

A **separate** run with six short quality checks before the long warm-up (W_SP8ddQ) reached Prefill 3741.8 / Decode 95.64 tok/s, TTFT 4.381 s, wall 25.794 s. Content checks passed 6/6; format checks 5/6 (JSON wrapped in Markdown). This is not evidence that running quality checks causes a speed increase. The main table does not select this faster run as the headline result.

## Limits

This is a prototype for review, tested on a single heterogeneous two-GPU desktop. It does not establish numerical/logit parity, long-form quality equivalence, statistical significance, multi-request concurrency, multi-model lifetime safety, or support for other GPU topologies, Windows or AMD. The embedding-table handoff uses process-global storage and needs further lifecycle review before general use. No measured run is a fixed-output-token replay. The existing MMQ over-read warning remains; Compute Sanitizer has not been run. The basic quality checks are not a comprehensive model evaluation.

The clean-base apply/build and repository-check results are recorded separately in `validation-summary.json`.
