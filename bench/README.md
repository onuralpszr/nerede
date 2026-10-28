# Bench notes

Measured on the speaker laptop: Intel Core Ultra X7 358H (Panther Lake), Arc B390 iGPU, Intel NPU, 32 GB RAM, Fedora 45. Text-only model (270M), 8 short queries, batch size 1.

| Runtime | Load | ms/query | Agreement with torch (cosine) |
|---|---|---|---|
| torch CPU (bf16) | 4.8 s | 23 | 1.0000 |
| torch XPU (Arc B390) | 2.5 s | 43 | 1.0000 |
| LiteRT CPU (int4 QAT, 165 MB) | 0.3 s | 40 | 0.988 |
| LiteRT GPU (WebGPU over Vulkan) | 0.6 s | 17 | 0.985 |
| OpenVINO GPU (static 256 tokens) | 13 s first run, then cached | 6.6 | 1.0000 |
| OpenVINO CPU (static 256 tokens) | 3.6 s | 187 | 1.0000 |
| Browser WebGPU q4 (default), Chrome on Arc B390 | 175 MB download | 160 | 0.98 |
| Browser WebGPU fp16 | 543 MB download | 31 | 1.0000 |
| Browser WebGPU q4f16 | 157 MB download | 29 | 0.91 |
| Browser WASM fp16 | 543 MB download | 116 | 1.0000 |

Indexing throughput (256 docs, batch 32): torch CPU 61 docs/s, torch XPU 176 docs/s.

Photo indexing (vision encoder, 280 tokens per image): CPU 257 s for 100 photos, XPU 16 s for 100 photos (batch 1, cosine 0.9995 or better vs CPU). This needs the int32 workaround in `nerede/embedders.py`, see draft issue 3.

Serving container (`podman build -t nerede .`): ~575 MB image, 1.1 s cold start, 204 MB RAM, about 80 ms per request on CPU (query embedding plus intent routing).

Retrieval quality (66 TR/EN queries, mostly cross-lingual, over 141 documents, index built with torch):

| dim | recall@1 torch | recall@3 torch | MRR torch | recall@1 LiteRT queries |
|---|---|---|---|---|
| 768 | 0.86 | 0.98 | 0.920 | 0.85 |
| 512 | 0.83 | 1.00 | 0.902 | 0.80 |
| 256 | 0.79 | 0.98 | 0.877 | 0.73 |
| 128 | 0.74 | 0.86 | 0.814 | 0.70 |

## Scripts

- `openvino_npu.py` converts the torch text model to OpenVINO and runs it on CPU, GPU and NPU.
- `photos_bench.py` times photo indexing on a torch device.
- `vision_xpu_repro.py` shows the XPU int64 `max(dim)` bug behind draft issue 3.
- `browser_test.mjs` drives the web UI in headless Chrome and searches in Browser mode.
- `browser_time.mjs` times Browser mode queries in a real Chrome window (headless Chrome gets a software WebGPU adapter).
- `browser_vectors.mjs` saves browser query vectors so they can be compared with PyTorch.

## NPU status

- LiteRT-LM NPU: `RuntimeError: NPU is supported only for Intel OpenVINO on Windows. Current platform is 'linux'.` The `_Intel_PTL.litertlm` file is meant for Windows.
- OpenVINO NPU on Linux: CPU and GPU work, NPU compile fails inside the driver (see draft issue 1).

## Draft issue 1 (openvinotoolkit/openvino)

**Title:** NPU compile fails for EmbeddingGemma 2 text model on Panther Lake

EmbeddingGemma 2 text model (google/embeddinggemma-2, text only) converted with `ov.convert_model` from PyTorch compiles and runs correctly on CPU and GPU (cosine 1.0 vs PyTorch) but fails to compile on NPU with static shape [1, 128]. Setup: Core Ultra X7 358H, Fedora 45, openvino 2026.4.1 (pip), intel-npu-driver 1.38.0.

Repro: `python bench/openvino_npu.py NPU`

```
Exception from src/plugins/intel_npu/src/compiler_adapter/src/ze_graph_ext_wrappers.cpp:425:
Compilation failed. Level0 pfnCreate2 result: ZE_RESULT_ERROR_INVALID_ARGUMENT, code 0x78000004 - generic error code for invalid arguments . [NPU_DRV] Driver reports a failure from vclAllocatedExecutableCreate4, return code: 2013265924
[NPU_VCL] Compiler returned msg:
Compilation failed
```

## Draft issue 2 (openvinotoolkit/openvino)

**Title:** Wrong embeddings for onnx-community/embeddinggemma-2-ONNX on CPU

Reading `onnx/model_fp16.onnx` from onnx-community/embeddinggemma-2-ONNX with `core.read_model` and running text only (empty `[0, 512]` image, video and audio feature inputs) returns embeddings with cosine 0.59 to 0.83 against the same model in onnxruntime (transformers.js) and LiteRT, which agree with each other at 0.98. Forcing `INFERENCE_PRECISION_HINT=f32` gives the same result, padding does not change it. Converting from PyTorch instead gives correct output.

Repro:

```python
import numpy as np, openvino as ov
from transformers import AutoTokenizer
p = "models/embeddinggemma-2-onnx"  # hf download onnx-community/embeddinggemma-2-ONNX --local-dir ...
tok = AutoTokenizer.from_pretrained(p)
cm = ov.Core().compile_model(f"{p}/onnx/model_fp16.onnx", "CPU")
e = tok(["title: none | text: Balık ekmek, Eminönü'nde satılan balık sandviçidir."], return_tensors="np")
z = np.zeros((0, 512), np.float32)
out = cm({"input_ids": e["input_ids"], "attention_mask": e["attention_mask"],
          "image_features": z, "video_features": z, "audio_features": z})["sentence_embedding"]
# compare with onnxruntime on the same file: cosine is far from 1.0
```

Side note: `read_model` refuses the file when it sits in the Hugging Face cache because `model_fp16.onnx_data` is a symlink into `blobs/`. Downloading with `--local-dir` avoids it.

## Draft issue 3 (intel/torch-xpu-ops)

**Title:** max(dim) and argmax on int64 tensors return wrong values on XPU

On torch 2.15.0+xpu (Arc B390, Fedora 45), `Tensor.max(dim=-1)` and `argmax` on an int64 tensor skip about a third of the elements, while `amax`, `max()` without dim, int32 and float32 are all correct. This breaks the EmbeddingGemma 2 vision pooler in transformers 5.21.0, which takes the patch grid width from an int64 max, so some photos fail with a `split_with_sizes` error.

Repro: `python bench/vision_xpu_repro.py`

```python
import torch
x = torch.zeros((1, 2520), dtype=torch.int64)
x[0, 2000] = 7
x = x.to("xpu")
print(x.max(dim=-1).values.item(), x.argmax(-1).item(), x.amax(-1).item())  # 0 0 7, expected 7 2000 7
```

```
RESULT torch.int64: max(dim=-1) missed 832 of 2520 positions, first [32, 33, 34]
RESULT torch.int32: max(dim=-1) missed 0 of 2520 positions, first []
RESULT torch.float32: max(dim=-1) missed 0 of 2520 positions, first []
```
