# Kurulum

**Python 3.12 veya 3.13**, [uv](https://docs.astral.sh/uv/) ve yaklaşık **3 GB disk** yeterli. GPU gerekmez.

!!! warning "Bunu evde yap, konferans Wi-Fi'ında değil"
    0. adım yaklaşık 1,7 GB model indirir. Atölyeden önce çalıştır.

```bash
# 1. uv (zaten varsa atla)
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

# 2. atölye
git clone https://github.com/onuralpszr/nerede && cd nerede
uv run workshop/00_setup_check.py
```

`uv run` ortamı ilk çalıştırmada kendisi kurar. Şuna benzer bir çıktı görmelisin:

```text
python   3.13.x
torch    2.15.0+cpu
device   cpu   (cuda = NVIDIA or AMD ROCm, xpu = Intel GPU, mps = Apple)
...
embedding shape (1, 768), norm 1.000. You are ready.
```

## PyTorch sürümünü seç

Varsayılan olarak **yalnızca CPU'lu PyTorch** gelir (CUDA'lı 5+ GB yerine 1,5 GB'lık ortam). Bu atölye için yeterli.
GPU'n varsa ve kullanmak istersen:

| Donanım | Komut | Cihaz |
|---|---|---|
| Herhangi bir dizüstü (varsayılan) | `uv run ...` | `cpu` |
| NVIDIA GPU (Linux) | `uv run --no-default-groups ...` | `cuda` |
| Intel Arc / Core Ultra GPU | `uv run --no-default-groups --group xpu ...` | `xpu` |
| AMD GPU | ROCm sürümünü [pytorch.org](https://pytorch.org/get-started/locally/) üzerinden kur | `cuda` |
| Apple Silicon | `uv run ...` | `mps` |
| Intel OpenVINO (CPU/GPU) | `--extra intel` ekle | yok |

Cihazı `nerede/embedders.py` içindeki `pick_torch_device()` kendisi seçer.
GPU sürümünü CPU sürümünün yanında tutmak için ona ayrı bir ortam ver:

```bash
UV_PROJECT_ENVIRONMENT=.venv-xpu uv run --no-default-groups --group xpu workshop/06_runtimes.py torch:cpu torch:xpu
```

## Windows { #windows }

Bütün `uv run ...` komutları PowerShell ve cmd'de aynı çalışıyor. Sadece ortam değişkenleri farklı yazılıyor:

=== "PowerShell"

    ```powershell
    $env:NEREDE_BACKEND = "litert"
    uv run uvicorn app.main:app

    $env:UV_PROJECT_ENVIRONMENT = ".venv-xpu"
    uv run --no-default-groups --group xpu workshop/06_runtimes.py torch:cpu torch:xpu

    Remove-Item Env:NEREDE_BACKEND, Env:UV_PROJECT_ENVIRONMENT   # varsayılanlara dön
    ```

=== "cmd"

    ```bat
    set NEREDE_BACKEND=litert
    uv run uvicorn app.main:app
    ```

=== "macOS / Linux"

    ```bash
    NEREDE_BACKEND=litert uv run uvicorn app.main:app
    ```

Böyle ayarlanan bir değişken terminali kapatana kadar geçerli. Windows için iki not daha:

- **NVIDIA**: PyPI'daki PyTorch Windows'ta yalnızca CPU'lu, yani `--no-default-groups` sana CUDA vermiyor. CUDA'lı sürümü
  [pytorch.org](https://pytorch.org/get-started/locally/) adresinden ortama kur.
- **Intel NPU**: LiteRT-LM'in NPU desteği Windows'u hedefliyor (bkz. [Ölçümler](benchmarks.md#npu)). Biz yalnızca Linux'ta
  deneyebildik, orada yok.

## Neler indiriliyor

| Model | Boyut | Ne için |
|---|---|---|
| `google/embeddinggemma-2` | ~1,5 GB | PyTorch: indeksleme, defterler (metin 270M, fotoğraflar için + görsel 170M) |
| `litert-community/embeddinggemma-2-text-270m-litert-lm` | 165 MB | LiteRT: sunucu ve 5. bölüm |
| `onnx-community/embeddinggemma-2-ONNX` (q4 metin) | ~175 MB | tarayıcı; sayfa kendisi indirir |

Üçü de Apache 2.0 lisanslı ve Hugging Face girişi gerektirmiyor.

## Proje yapısı

```text
data/       yerler (TR + EN), DevFest bilgileri, EmbeddingGemma notları, fotoğraflar, değerlendirme soruları
nerede/     kütüphane: önekler, embedder'lar (torch, LiteRT, OpenVINO), indeks, yönlendirici
workshop/   numaralı adımlar, her biri tek fikir
notebooks/  aynı adımlar Colab defteri olarak (İngilizce ve Türkçe)
app/        FastAPI sunucusu ve web arayüzü (sunucuda ya da tarayıcıda çıkarım)
docs/       bu site (Zensical, İngilizce ve Türkçe)
scripts/    yardımcılar: fotoğrafları indir, silueti çiz, dokümanı derle
bench/      konuşmacının dizüstünde yapılan ölçümler
```
