# 3. Measure, don't guess

"It looks good" is not a metric. `data/eval_queries.jsonl` has 66 questions, each with the id of the
document that should come first. Most are **cross-lingual**: a Turkish question for an English document,
or the other way round.

```bash
uv run workshop/04_matryoshka_eval.py
uv run workshop/04_matryoshka_eval.py --query-backend litert   # torch index, LiteRT queries
```

```text
index: torch:cpu   queries: torch:cpu   n=66

  dim  recall@1  recall@3    MRR  bytes/vec   1M docs
  768      0.86      0.98  0.920       3072    2.86GB
  512      0.83      1.00  0.902       2048    1.91GB
  256      0.79      0.98  0.877       1024    0.95GB
  128      0.74      0.86  0.814        512    0.48GB
```

- **recall@1**: how often the right answer is first. **recall@3**: in the top three.
- **MRR**: mean reciprocal rank, 1.0 means always first, 0.5 means usually second.

## Matryoshka: smaller vectors, almost the same answers

EmbeddingGemma 2 is trained so that the **first** 512, 256 or 128 numbers of a vector are already a good
embedding. Keep the start, then re-normalize:

```python
def truncate(v, dim):
    v = v[..., :dim]
    return v / np.linalg.norm(v, axis=-1, keepdims=True)   # skipping this quietly hurts ranking
```

Queries and documents must use the **same** size. At 256d we keep 98% recall@3 with a third of the storage.
128d is a 6x saving, but the drop is visible. That is why you measure on your own data.

## Read the misses

The script prints every question it got wrong at 768d. They are the most interesting part:

```text
miss: "Mimar Sinan'ın en ünlü camisi" -> semsi-pasa (expected suleymaniye)
miss: "when is the conference this year" -> devfest-2025-stats (expected devfest-ne-zaman)
```

Şemsi Paşa is also a Sinan mosque, and "this year" is hard to match when two documents both talk about a year.
Often the fix is in the data (a clearer document) rather than in the model.

## Try it

- [ ] Write five questions of your own into `data/eval_queries.jsonl`. Which ones fail?
- [ ] Improve one document so that a miss becomes a hit. Rebuild and rerun.
