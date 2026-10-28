"""Step 2: embed every document and photo once, save the index (plus a small JSON copy for the browser).

uv run workshop/02_build_index.py                  # torch, auto device, text + photos
uv run workshop/02_build_index.py --no-images      # text only (270M, faster)
uv run workshop/02_build_index.py --backend litert:gpu --no-images
"""

import argparse
import time

from nerede import Index, get_embedder, load_corpus, load_images
from nerede.embedders import TorchEmbedder
from nerede.index import INDEX, ROOT
from nerede.router import Router

parser = argparse.ArgumentParser()
parser.add_argument("--backend", default=None, help="torch | torch:xpu | litert | litert:gpu | openvino:GPU")
parser.add_argument(
    "--no-images",
    action="store_true",
    help="do not embed the photos (no vision encoder needed), keep the photo vectors already in the index",
)
parser.add_argument("--web-dim", type=int, default=256, help="Matryoshka size for the browser copy")
args = parser.parse_args()

docs = load_corpus()
images = [] if args.no_images else load_images()
want_vision = bool(images)

# One torch model with the vision encoder can embed both text and photos (440M params).
backend = args.backend or "torch"
embedder = get_embedder(backend, modalities=("text", "image") if want_vision else ("text",))
start = time.perf_counter()
index = Index.build(embedder, docs)
print(f"{len(docs)} documents embedded with {embedder.name} in {time.perf_counter() - start:.1f}s")

if want_vision:
    vision = embedder if isinstance(embedder, TorchEmbedder) else TorchEmbedder(modalities=("text", "image"))
    start = time.perf_counter()
    index.add_images(vision, images)
    print(f"{len(images)} photos embedded with {vision.name} in {time.perf_counter() - start:.1f}s")
elif INDEX.exists():
    # Photo vectors live in the same space as text, so the ones in the shipped index stay valid.
    previous = Index.load(INDEX)
    index.images, index.image_vectors = previous.images, previous.image_vectors
    print(f"{len(index.images)} photo vectors kept from {INDEX.relative_to(ROOT)}")

index.save(INDEX)
web = ROOT / "app" / "static" / "index.json"
index.export_web(web, dim=args.web_dim, router=Router(embedder))  # router labels let Browser mode do hybrid search
print(f"index -> {INDEX.relative_to(ROOT)}")
print(f"browser copy at {args.web_dim}d -> {web.relative_to(ROOT)} ({web.stat().st_size / 1024:.0f} KB)")
