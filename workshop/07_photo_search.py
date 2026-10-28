"""Bonus: text-to-photo search over a folder of your own pictures. Nothing leaves your laptop.

Loads the vision encoder too (440M params). Images get NO prompt; text queries do.

    uv run workshop/07_photo_search.py ~/Pictures
"""

import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

from nerede.embedders import pick_torch_device

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "~/Pictures").expanduser()
photos = sorted(p for p in folder.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})[:200]
if not photos:
    sys.exit(f"no images found in {folder}")

model = SentenceTransformer("google/embeddinggemma-2", device=pick_torch_device(), config_kwargs={"audio_config": None})
print(f"embedding {len(photos)} photos from {folder} ...")
photo_emb = model.encode([{"image": str(p)} for p in photos], batch_size=8, show_progress_bar=True)

while text := input("\nfind photo > ").strip():
    scores = model.similarity(model.encode(text, prompt_name="SearchQuery"), photo_emb)[0]
    for i in scores.argsort(descending=True)[:5]:
        print(f"  {scores[i]:.3f}  {photos[i]}")
