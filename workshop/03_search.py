"""Step 3: search the index from your terminal. Ask in Turkish or English.

uv run workshop/03_search.py
uv run workshop/03_search.py --collection devfest devfest2025
uv run workshop/03_search.py --photos            # text -> photo search
uv run workshop/03_search.py --dim 128 --backend litert
uv run workshop/03_search.py --vector-only      # turn off the hybrid boosts for short queries
"""

import argparse

from nerede import Index, get_embedder, query
from nerede.router import Router

parser = argparse.ArgumentParser()
parser.add_argument("--backend", default=None)
parser.add_argument("--dim", type=int, default=768, choices=[768, 512, 256, 128])
parser.add_argument(
    "--collection", nargs="+", default=["all"], choices=["all", "places", "devfest", "devfest2025", "gemma"]
)
parser.add_argument("--photos", action="store_true", help="search the photos instead of the text")
parser.add_argument("-k", type=int, default=3)
parser.add_argument("--vector-only", action="store_true", help="no intent or keyword boosts for short queries")
args = parser.parse_args()

index = Index.load()
embedder = get_embedder(args.backend)
router = None if args.vector_only else Router(embedder)
print(
    f"{len(index.docs)} docs, {len(index.images)} photos, built with {index.built_with}. "
    f"Querying with {embedder.name} at {args.dim}d. Empty line quits.\n"
)

while text := input("nerede? > ").strip():
    q = embedder.embed([query(text)])[0]
    if args.photos:
        for score, img in index.search_images(q, k=args.k, dim=args.dim):
            print(f"  {score:.3f}  {img['title']}  data/images/{img['file']}")
    else:
        hybrid = {} if router is None else {"text": text, "intent": router.route(text)}
        for score, doc in index.search(q, k=args.k, dim=args.dim, collection=args.collection, **hybrid):
            where = doc.get("district") or doc["collection"]
            print(f"  {score:.3f}  {doc['title']}  ({where}, {doc['category']})")
    print()
