# Setup

You need **Python 3.12 or 3.13**, [uv](https://docs.astral.sh/uv/) and about **3 GB of disk**.
No GPU is required.

!!! warning "Do this at home, not on conference Wi-Fi"
    Step 0 downloads about 1.7 GB of models. Run it before the workshop.

```bash
# 1. uv (skip if you already have it)
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

# 2. the workshop
git clone https://github.com/onuralpszr/nerede && cd nerede
uv run workshop/00_setup_check.py
```

`uv run` creates the environment on first use. You should see something like:

```text
python   3.13.x
torch    2.15.0+cpu
device   cpu   (cuda = NVIDIA or AMD ROCm, xpu = Intel GPU, mps = Apple)
...
embedding shape (1, 768), norm 1.000. You are ready.
```

## Pick your PyTorch build

By default you get **CPU-only PyTorch** (a 1.5 GB environment instead of 5+ GB with CUDA). That is all this workshop needs.
If you have a GPU and want to use it:

| Hardware | Command | Device |
|---|---|---|
| Any laptop (default) | `uv run ...` | `cpu` |
| NVIDIA GPU (Linux) | `uv run --no-default-groups ...` | `cuda` |
| Intel Arc / Core Ultra GPU | `uv run --no-default-groups --group xpu ...` | `xpu` |
| AMD GPU | install the ROCm wheel from [pytorch.org](https://pytorch.org/get-started/locally/) | `cuda` |
| Apple Silicon | `uv run ...` | `mps` |
| Intel OpenVINO (CPU/GPU) | add `--extra intel` | n/a |

The device is picked automatically by `pick_torch_device()` in `nerede/embedders.py`.
To keep a GPU build next to the CPU one, give it its own environment:

```bash
UV_PROJECT_ENVIRONMENT=.venv-xpu uv run --no-default-groups --group xpu \
  workshop/06_runtimes.py torch:cpu torch:xpu
```

## Windows { #windows }

Every `uv run ...` command works the same in PowerShell and cmd. Only environment variables are written differently:

=== "PowerShell"

    ```powershell
    $env:NEREDE_BACKEND = "litert"
    uv run uvicorn app.main:app

    $env:UV_PROJECT_ENVIRONMENT = ".venv-xpu"
    uv run --no-default-groups --group xpu `
      workshop/06_runtimes.py torch:cpu torch:xpu

    # back to the defaults
    Remove-Item Env:NEREDE_BACKEND, Env:UV_PROJECT_ENVIRONMENT
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

A variable set this way lasts until you close the terminal. Two more Windows notes:

- **NVIDIA**: PyTorch from PyPI is CPU-only on Windows, so `--no-default-groups` does not give you CUDA. Install the CUDA
  build from [pytorch.org](https://pytorch.org/get-started/locally/) into the environment instead.
- **Intel NPU**: LiteRT-LM's NPU backend targets Windows (see [Benchmarks](benchmarks.md#npu)). We could only test Linux,
  where it is not available.

## What gets downloaded

| Model | Size | Used for |
|---|---|---|
| `google/embeddinggemma-2` | ~1.5 GB | PyTorch: indexing, notebooks (text 270M, + vision 170M for photos) |
| `litert-community/embeddinggemma-2-text-270m-litert-lm` | 165 MB | LiteRT: the server and step 5 |
| `onnx-community/embeddinggemma-2-ONNX` (q4 text) | ~175 MB | the browser, downloaded by the page itself |

All three are Apache 2.0 and need no Hugging Face login.

## Project layout

```text
data/       places (TR + EN), DevFest, EmbeddingGemma notes, photos, eval sets
nerede/     the library: prompts, embedders, index, router, keywords
workshop/   numbered steps, one idea each
notebooks/  the same steps as Colab notebooks (English and Turkish)
app/        FastAPI server and the web UI (server or browser inference)
docs/       this site (Zensical, English and Turkish)
scripts/    helpers in draw/, data/, docs/ and notebooks/
bench/      measurements from the speaker laptop
```
