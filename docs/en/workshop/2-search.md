# 2. Index and search

Embed every document **once**, keep the vectors, and at query time embed only the question.
That is all a semantic search index is.

```bash
uv run workshop/02_build_index.py --no-images     # 141 docs, ~15 s on a laptop CPU
uv run workshop/03_search.py                       # ask in Turkish or English
uv run workshop/03_search.py --collection devfest
uv run workshop/03_search.py --photos              # text -> photo (needs the photo index)
```

!!! info "Photos take longer"
    Without `--no-images`, step 2 also loads the vision encoder and embeds 100 photos. That takes about
    4 minutes on a laptop CPU and under a minute on a GPU. The repository already ships a prebuilt index
    with photos, so you can skip this and still use photo search.

## The index is just numpy

```python
texts = [document(d["text"], title=d["title"]) for d in docs]
vectors = embedder.embed(texts)                    # (141, 768), unit length

q = embedder.embed([query("balık ekmek nerede yenir")])[0]
scores = vectors @ q                               # cosine similarity, since everything is normalized
best = scores.argsort()[::-1][:5]
```

`nerede/index.py` adds three things on top: collection filters, photo vectors, and Matryoshka truncation.
For tens of thousands of documents this is fast enough. Use Qdrant, sqlite-vec or pgvector when you need
millions of vectors, persistence or rich filtering.

## Titles matter

Documents are embedded as `title: Balık ekmek | text: ...` instead of `title: none | text: ...`.
The model card recommends real titles when you have them, and they help short documents a lot.

## Try it

- [ ] Search `"rainy day"` with `--collection places`, then with `all`.
- [ ] Ask the same question in Turkish and in English. Do you get the same top result?
- [ ] Add your favourite place to `data/istanbul.jsonl`, rebuild, and find it.
