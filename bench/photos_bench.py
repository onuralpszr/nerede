"""Time photo indexing (vision encoder) on a given torch device: uv run bench/photos_bench.py xpu"""

import sys
import time

from nerede.embedders import TorchEmbedder
from nerede.index import DATA, load_images

images = load_images()
emb = TorchEmbedder(device=sys.argv[1] if len(sys.argv) > 1 else None, modalities=("text", "image"))
emb.embed_images([str(DATA / "images" / images[0]["file"])])  # warm-up
start = time.perf_counter()
emb.embed_images(
    [str(DATA / "images" / i["file"]) for i in images], batch_size=int(sys.argv[2]) if len(sys.argv) > 2 else 8
)
print(f"RESULT {emb.name}: {len(images)} photos in {time.perf_counter() - start:.1f}s")
