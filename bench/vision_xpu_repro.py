"""Minimal repro: torch.max(dim=...) on int64 skips elements on XPU. uv run bench/vision_xpu_repro.py

This is why the EmbeddingGemma 2 vision pooler failed on some photos on XPU (it takes the grid
width from an int64 max). nerede.embedders works around it by running that step in int32.
"""
import torch

n = 2520  # patches for one 800x800 photo
for dtype in [torch.int64, torch.int32, torch.float32]:
    missed = []
    for i in range(n):
        x = torch.zeros((1, n), dtype=dtype)
        x[0, i] = 7
        if x.to("xpu").max(dim=-1).values.item() != 7:
            missed.append(i)
    print(f"RESULT {dtype}: max(dim=-1) missed {len(missed)} of {n} positions, first {missed[:3]}")

x = torch.zeros((1, n), dtype=torch.int64)
x[0, 2000] = 7
x = x.to("xpu")
print(f"max(dim) {x.max(dim=-1).values.item()}  argmax {x.argmax(-1).item()}  amax {x.amax(-1).item()}  max() {x.max().item()}")
print(f"torch {torch.__version__}")
