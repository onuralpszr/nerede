# 7. Photo search

EmbeddingGemma 2 puts **images, audio and video in the same 768d space as text**.
So a photo indexed once with the vision encoder can be found later with nothing but words, and even by the
small text-only LiteRT model on the server.

```bash
uv run workshop/03_search.py --photos          # the 106 Istanbul photos
uv run workshop/07_photo_search.py ~/Pictures  # your own photos, nothing leaves your laptop
```

## How it works

```python
model = SentenceTransformer("google/embeddinggemma-2", config_kwargs={"audio_config": None})  # text + vision, 440M

photo_vectors = model.encode([{"image": "data/images/galata-kulesi.jpg"}, ...])   # no prompt for media
query_vector = model.encode("a stone tower by the sea", prompt_name="SearchQuery")
model.similarity(query_vector, photo_vectors)
```

Two rules:

1. **Media get no task prefix.** Only text does.
2. Inside text, `<|image|>`, `<|video|>` and `<|audio|>` are placeholders for media. If a document *talks about*
   these markers, escape them, or the processor will wait for an image that never comes
   (`nerede/prompts.py` does this for you).

## The photos

The 106 photos come from Wikimedia Commons under CC BY, CC BY-SA, Free Art License or public domain.
`scripts/fetch_images.py` takes the lead image of each place's Wikipedia article, checks the license and
writes the credits to `data/images/ATTRIBUTION.md`. The app shows the author and license under every photo.

## Try it

- [ ] Turn on only the **Photos** filter and search `"street food"`. Which dishes come up?
- [ ] Search with a Turkish phrase: `"deniz kenarında taş kule"`.
- [ ] Mix modalities: `model.encode({"text": "A day out <|image|>", "image": "photo.jpg"})` embeds a post with its photo as one vector.
