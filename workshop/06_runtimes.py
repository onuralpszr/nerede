"""Step 6: one vector space, many runtimes. Same queries, compare speed and agreement with torch.

    uv run workshop/06_runtimes.py torch litert litert:gpu
    uv run --extra intel workshop/06_runtimes.py torch:cpu torch:xpu litert litert:gpu openvino:GPU
"""

import sys
import time

from nerede import get_embedder, query

texts = [query(t) for t in [
    "where can I eat a fish sandwich?", "Bizans mozaikleri", "train under the Bosphorus",
    "ormanda koşu", "rainy day ideas", "Mimar Sinan'ın camisi", "tulip festival", "eski kitaplar",
]]
specs = sys.argv[1:] or ["torch", "litert", "litert:gpu"]

reference = None
print(f"{'runtime':>14} {'load':>7} {'ms/query':>9} {'cos vs first':>13}")
for spec in specs:
    try:
        start = time.perf_counter()
        emb = get_embedder(spec)
        load = time.perf_counter() - start
        emb.embed(texts[:1])  # warm-up
        start = time.perf_counter()
        vectors = [emb.embed([t])[0] for t in texts]
        ms = (time.perf_counter() - start) / len(texts) * 1000
    except Exception as exc:  # e.g. no GPU, missing driver
        print(f"{spec:>14}  skipped: {str(exc).splitlines()[0][:80]}")
        continue
    if reference is None:
        reference = vectors
    agree = sum(float(a @ b) for a, b in zip(vectors, reference)) / len(texts)
    print(f"{emb.name:>14} {load:>6.1f}s {ms:>9.1f} {agree:>13.4f}")
