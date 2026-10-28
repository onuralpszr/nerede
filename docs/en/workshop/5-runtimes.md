# 5. One vector space, many runtimes

The same model ships in several formats. As long as they produce the same vectors, you can build the index
with one and query it with another.

```bash
uv run workshop/06_runtimes.py torch litert litert:gpu
uv run --extra intel workshop/06_runtimes.py \
  torch litert litert:gpu openvino:GPU
```

```text
       runtime    load  ms/query  cos vs first
     torch:cpu    4.8s      23.3        1.0000
    litert:cpu    0.3s      40.4        0.9881
    litert:gpu    0.6s      16.7        0.9854
  openvino:GPU   13.4s       6.6        1.0000
```

*Measured on an Intel Core Ultra laptop with an Arc iGPU. Your numbers will differ, the shape will not.*

| Spec | Runtime | When to use it |
|---|---|---|
| `torch`, `torch:xpu`, `torch:cuda` | sentence-transformers | indexing in batches, notebooks, fine-tuning |
| `litert`, `litert:gpu` | LiteRT-LM, int4 QAT `.litertlm` (165 MB) | servers without PyTorch, phones, Raspberry Pi |
| `openvino:GPU` | OpenVINO, converted from PyTorch on first run | Intel GPUs and NPUs |
| browser | transformers.js, ONNX q4 (~175 MB) | no server at all |

## LiteRT in four lines

```python
import litert_lm
from huggingface_hub import hf_hub_download

path = hf_hub_download(
    "litert-community/embeddinggemma-2-text-270m-litert-lm",
    "embeddinggemma-2-text-270m.litertlm",
)
with litert_lm.EmbeddingEngine(path, backend=litert_lm.Backend.GPU()) as engine:
    vector = engine.compute_embedding(
        "task: search result | query: balık ekmek"
    ).embedding
```

The same `.litertlm` file runs on Android, iOS, macOS, Linux, Windows and the web.

## Why "cos vs first" matters

`0.988` means the LiteRT vector points almost the same way as the PyTorch one. The eval proves it is enough:
with a PyTorch-built index and LiteRT queries, recall@1 stays at 0.83, the same as PyTorch. That is what lets the server run
without PyTorch.

!!! note "Intel NPU"
    LiteRT-LM supports the Intel NPU on Windows. On Linux the OpenVINO NPU compiler does not accept this model
    yet (see [Benchmarks](../benchmarks.md)). CPU and GPU work everywhere.
