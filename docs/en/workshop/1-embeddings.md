# 1. Embeddings

An **embedding** is a list of numbers (here 768 of them) that represents what a piece of content *means*.
Texts with similar meanings get vectors that point in similar directions, so *"where can I eat a fish sandwich?"*
and *"Balık ekmek, Eminönü'nde satılan balık sandviçi"* end up close together, even though they share no words and use different languages.

```bash
uv run workshop/00_setup_check.py
uv run workshop/01_hello_embeddings.py
```

## Load only what you need

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "google/embeddinggemma-2",
    # text only: 270M instead of 740M
    config_kwargs={"vision_config": None, "audio_config": None},
)
```

## Task prompts

EmbeddingGemma 2 was trained with short prefixes that tell it what the vector is for.
Search is **asymmetric**: queries and documents get different prefixes.

| Use | Query | Document |
|---|---|---|
| search | `task: search result \| query: {q}` | `title: {title} \| text: {content}` |
| question answering | `task: question answering \| query: {q}` | same as above |
| code search | `task: code retrieval \| query: {q}` | `title: {file} \| text: {code}` |
| classification, clustering, similarity | `task: classification \| query: {text}` (same on both sides) | |

sentence-transformers knows the common ones by name:

```python
# "title: none | text: "
doc_emb = model.encode(documents, prompt_name="Document")
# "task: search result | query: "
query_emb = model.encode(queries, prompt_name="SearchQuery")
# cosine similarity
scores = model.similarity(query_emb, doc_emb)
```

This project's code builds the strings itself (`nerede/prompts.py`), so that it can use real titles and
send the same text to every runtime.

## Try it

- [ ] Remove `prompt_name=` from both `encode()` calls. Do the scores get worse?
- [ ] Add a sentence in another language you speak. Does it still find the right document?
- [ ] Compare `"bank"` with `"river bank"` and `"money bank"`. What does that tell you about context?
