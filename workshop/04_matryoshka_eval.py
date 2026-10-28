"""Step 4: measure, don't guess. How much quality do smaller vectors and other runtimes cost?

Uses hand-labelled TR/EN queries (data/eval_queries.jsonl), most of them cross-lingual.

    uv run workshop/04_matryoshka_eval.py
    uv run workshop/04_matryoshka_eval.py --query-backend litert   # torch index, LiteRT queries
"""

import argparse
import json

import numpy as np

from nerede import Index, get_embedder, query
from nerede.index import ROOT, truncate

parser = argparse.ArgumentParser()
parser.add_argument("--query-backend", default=None, help="defaults to the same runtime as the index, on this machine's best device")
args = parser.parse_args()

index = Index.load()
evals = [json.loads(line) for line in (ROOT / "data" / "eval_queries.jsonl").read_text().splitlines() if line]
# built_with is e.g. "torch:xpu"; keep the runtime but let this machine pick its own device
embedder = get_embedder(args.query_backend or index.built_with.split(":")[0])
Q = embedder.embed([query(e["query"]) for e in evals])
ids = [d["id"] for d in index.docs]
gold = np.array([ids.index(e["gold"]) for e in evals])

print(f"index: {index.built_with}   queries: {embedder.name}   n={len(evals)}\n")
print(f"{'dim':>5} {'recall@1':>9} {'recall@3':>9} {'MRR':>6} {'bytes/vec':>10} {'1M docs':>9}")
for dim in (768, 512, 256, 128):
    scores = truncate(Q, dim) @ truncate(index.vectors, dim).T
    rank = (scores > scores[np.arange(len(gold)), gold][:, None]).sum(1)  # 0 = gold is first
    size = dim * 4  # float32; use 2 for float16/bfloat16
    print(f"{dim:>5} {np.mean(rank < 1):>9.2f} {np.mean(rank < 3):>9.2f} {np.mean(1 / (rank + 1)):>6.3f}"
          f" {size:>10} {size * 1e6 / 2**30:>7.2f}GB")

top = np.argmax(Q @ index.vectors.T, axis=1)
for e, t, g in zip(evals, top, gold):
    if t != g:
        print(f"  miss at 768d: {e['query']!r} -> {index.docs[t]['id']} (expected {e['gold']})")
