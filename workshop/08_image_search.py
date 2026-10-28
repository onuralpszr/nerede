"""Search by image: a photo goes in, the matching photos and places come out.

The query photo goes through the vision encoder with no prompt, like every indexed photo. Photos and texts share
one 768d space, so the same vector finds similar photos (image -> image) and the place descriptions (image -> text).

    uv run workshop/08_image_search.py data/query_images/galata-kulesi.jpg
    uv run workshop/08_image_search.py ~/Pictures/holiday.jpg --dim 256
    uv run workshop/08_image_search.py --eval        # every query photo: is the right place in the top 1 / top 3?

The query photos in data/query_images/ are *other* photos of the indexed places, so the model never saw them.
"""

import argparse

import numpy as np

from nerede import Index
from nerede.embedders import TorchEmbedder
from nerede.index import DATA, read_jsonl

parser = argparse.ArgumentParser()
parser.add_argument("photo", nargs="?", help="path to a .jpg or .png")
parser.add_argument("--dim", type=int, default=768, choices=[768, 512, 256, 128])
parser.add_argument("--eval", action="store_true", help="score all photos in data/query_images/")
parser.add_argument("-k", type=int, default=3)
parser.add_argument("--device", default=None, help="cuda, xpu, mps or cpu (default: the best one found)")
args = parser.parse_args()
if not args.photo and not args.eval:
    parser.error("give a photo, or --eval")

index = Index.load()
embedder = TorchEmbedder(device=args.device, modalities=("text", "image"))  # text + vision, 440M params

if args.photo:
    vector = embedder.embed_images([args.photo])[0]
    print(f"\nmatching places (photo and text both vote, {args.dim}d)")
    for score, doc in index.search_by_photo(vector, k=args.k, dim=args.dim):
        print(f"  {score:.3f}  {doc['title']}  ({doc['district']}, {doc['category']})")
    print("\nsimilar photos (image -> image)")
    for score, img in index.search_images(vector, k=args.k, dim=args.dim):
        print(f"  {score:.3f}  {img['title']}  data/images/{img['file']}")

if args.eval:
    queries = read_jsonl(DATA / "query_images.jsonl")
    vectors = embedder.embed_images([str(DATA / "query_images" / q["file"]) for q in queries])

    def rank(hits: list[tuple[float, dict]], place: str) -> int:
        ids = [item["id"] for _, item in hits]
        return ids.index(place) + 1 if place in ids else len(ids) + 1

    print(f"\n{len(queries)} query photos, right place in the top 1 / top 3")
    print(f"  {'dim':>4}  {'image -> image':>14}  {'image -> text':>13}  {'both':>11}")
    misses = []
    for dim in (768, 512, 256, 128):
        ranks = {"image": [], "text": [], "both": []}
        n = len(index.places)
        for q, v in zip(queries, vectors, strict=True):
            ranks["image"].append(rank(index.search_images(v, k=n, dim=dim), q["id"]))
            ranks["text"].append(rank(index.search(v, k=n, dim=dim, collection="places"), q["id"]))
            both = index.search_by_photo(v, k=n, dim=dim)
            ranks["both"].append(rank(both, q["id"]))
            if dim == args.dim and ranks["both"][-1] > 1:
                misses.append(f"  {q['id']:<18} rank {ranks['both'][-1]:>2}, top 1 was {both[0][1]['id']}")
        cells = [f"{np.mean(np.array(r) <= 1):.2f} / {np.mean(np.array(r) <= 3):.2f}" for r in ranks.values()]
        print(f"  {dim:>4}  {cells[0]:>14}  {cells[1]:>13}  {cells[2]:>11}")
    print(f"\nmisses at {args.dim}d (both):", *misses, sep="\n")
