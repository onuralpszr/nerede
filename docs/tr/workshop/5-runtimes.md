# 5. Tek vektör uzayı, birçok runtime

Aynı model birkaç farklı biçimde geliyor. Hepsi aynı vektörleri ürettiği sürece indeksi biriyle kurup
diğeriyle sorgulayabilirsin.

```bash
uv run workshop/06_runtimes.py torch litert litert:gpu
uv run --extra intel workshop/06_runtimes.py torch litert litert:gpu openvino:GPU
```

```text
       runtime    load  ms/query  cos vs first
     torch:cpu    4.8s      23.3        1.0000
    litert:cpu    0.3s      40.4        0.9881
    litert:gpu    0.6s      16.7        0.9854
  openvino:GPU   13.4s       6.6        1.0000
```

*Arc iGPU'lu bir Intel Core Ultra dizüstünde ölçüldü. Senin sayıların farklı olacak, tablo aynı kalacak.*

| Tanım | Runtime | Ne zaman |
|---|---|---|
| `torch`, `torch:xpu`, `torch:cuda` | sentence-transformers | toplu indeksleme, defterler, ince ayar |
| `litert`, `litert:gpu` | LiteRT-LM, int4 QAT `.litertlm` (165 MB) | PyTorch'suz sunucular, telefonlar, Raspberry Pi |
| `openvino:GPU` | OpenVINO, ilk çalıştırmada PyTorch'tan dönüştürülür | Intel GPU ve NPU'lar |
| tarayıcı | transformers.js, ONNX q4 (~175 MB) | hiç sunucu olmadan |

## Dört satırda LiteRT

```python
import litert_lm
from huggingface_hub import hf_hub_download

path = hf_hub_download("litert-community/embeddinggemma-2-text-270m-litert-lm", "embeddinggemma-2-text-270m.litertlm")
with litert_lm.EmbeddingEngine(path, backend=litert_lm.Backend.GPU()) as engine:
    vector = engine.compute_embedding("task: search result | query: balık ekmek").embedding
```

Aynı `.litertlm` dosyası Android, iOS, macOS, Linux, Windows ve web'de çalışıyor.

## "cos vs first" neden önemli

`0.988`, LiteRT vektörünün PyTorch vektörüyle neredeyse aynı yöne baktığı anlamına geliyor. Değerlendirme bunun yettiğini
gösteriyor: PyTorch ile kurulan indeksi LiteRT sorgularıyla aradığımızda recall@1 yine 0,85. Sunucunun PyTorch'suz
çalışabilmesini sağlayan şey bu.

!!! note "Intel NPU"
    LiteRT-LM, Intel NPU'yu Windows'ta destekliyor. Linux'ta OpenVINO NPU derleyicisi bu modeli henüz kabul etmiyor
    (bkz. [Ölçümler](../benchmarks.md)). CPU ve GPU her yerde çalışıyor.
