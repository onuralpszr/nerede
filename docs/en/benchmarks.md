# Benchmarks

Measured on the speaker laptop: Intel Core Ultra X7 358H, Arc B390 iGPU, Intel NPU, 32 GB RAM, Fedora.
Text-only model, short queries, batch size 1. Scripts are in `bench/` and `workshop/06_runtimes.py`.

## Query latency

| Runtime | Load | ms / query | Cosine vs PyTorch |
|---|---|---|---|
| PyTorch CPU (bf16) | 4.8 s | 23 | 1.0000 |
| PyTorch XPU (Arc B390) | 2.5 s | 43 | 1.0000 |
| LiteRT CPU (int4 QAT, 165 MB) | 0.3 s | 40 | 0.988 |
| LiteRT GPU (WebGPU over Vulkan) | 0.6 s | 17 | 0.985 |
| OpenVINO GPU (static 256 tokens) | 13 s first run, then cached | **6.6** | 1.0000 |
| Browser WebGPU, q4 (default) | 175 MB download | 160 | 0.98 |
| Browser WebGPU, fp16 (`?dtype=fp16`) | 543 MB download | 31 | 1.0000 |
| Browser WebGPU, q4f16 (`?dtype=q4f16`) | 157 MB download | 29 | 0.91 |
| Browser WASM, fp16 (no WebGPU) | 543 MB download | 116 | 1.0000 |

Browser rows: Chrome on the Arc B390 (`xe-3lpg` adapter, not the software fallback), median of 10 warm queries,
cosine against PyTorch over 8 queries (`bench/browser_time.mjs`, `bench/browser_vectors.mjs`). q4 stays the default because 175 MB
is kind to conference Wi-Fi; on a fast connection `?dtype=fp16` is 5× faster and exact. q4f16 is fast but changed the
top result for 3 of 8 queries, so we don't use it.

## Indexing

| Job | CPU | GPU |
|---|---|---|
| 256 short docs (text model, batch 32) | 61 docs/s | 176 docs/s (XPU) |
| 141 workshop docs | 14 s | |
| 100 photos (vision encoder, 280 tokens per image) | 257 s | 16 s (XPU, batch 1) |

## Retrieval quality

66 questions, mostly cross-lingual, over 141 documents. Index built with PyTorch.

| dim | recall@1 | recall@3 | MRR | recall@1, LiteRT queries |
|---|---|---|---|---|
| 768 | 0.86 | 0.98 | 0.920 | 0.85 |
| 512 | 0.83 | 0.98 | 0.900 | 0.80 |
| 256 | 0.79 | 0.98 | 0.877 | 0.71 |
| 128 | 0.76 | 0.86 | 0.822 | 0.70 |

## Serving

| | |
|---|---|
| Container image (FastAPI + LiteRT, no PyTorch) | ~575 MB |
| Cold start | ~1.1 s |
| RAM | ~200 MB |
| Request (query embedding + intent routing) | ~80 ms on CPU |

!!! note "XPU and photos"
    With torch 2.15 XPU, `max(dim=...)` on int64 tensors skips about a third of the elements. The vision encoder
    uses one to find the patch grid width, so some photos failed with a `split_with_sizes` error. `TorchEmbedder`
    runs that step in int32 on XPU, and all 100 photos then match CPU (cosine 0.9995 or better).
    Reproduction: `bench/vision_xpu_repro.py`.

## NPU

- **LiteRT-LM**: `NPU is supported only for Intel OpenVINO on Windows.` The `_Intel_PTL.litertlm` file targets Windows.
- **OpenVINO on Linux**: the model compiles and matches PyTorch exactly on CPU and GPU, but the NPU compiler rejects it
  (`ZE_RESULT_ERROR_INVALID_ARGUMENT`). Reproduction: `bench/openvino_npu.py`.
