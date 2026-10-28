"""Step 0: check your environment and pre-download the models (do this BEFORE the workshop Wi-Fi melts)."""

import platform

import torch
from huggingface_hub import hf_hub_download, snapshot_download

from nerede.embedders import LITERT_FILE, LITERT_REPO, MODEL_ID, pick_torch_device

print(f"python   {platform.python_version()}")
print(f"torch    {torch.__version__}")
print(f"device   {pick_torch_device()}   (cuda = NVIDIA or AMD ROCm, xpu = Intel GPU, mps = Apple)")

print(f"\ndownloading {MODEL_ID} (~1.5 GB, all modalities)...")
snapshot_download(MODEL_ID)
print(f"downloading {LITERT_REPO}/{LITERT_FILE} (~165 MB)...")
hf_hub_download(LITERT_REPO, LITERT_FILE)

from nerede import get_embedder, query  # noqa: E402

vec = get_embedder("torch").embed([query("Merhaba DevFest İstanbul!")])
print(f"\nembedding shape {vec.shape}, norm {float((vec**2).sum()) ** 0.5:.3f}. You are ready.")
