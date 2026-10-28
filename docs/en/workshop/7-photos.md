# 7. Photo search

EmbeddingGemma 2 puts **images, audio and video in the same 768d space as text**.
So a photo indexed once with the vision encoder can be found later with nothing but words, and even by the
small text-only LiteRT model on the server.

```bash
# the 106 Istanbul photos
uv run workshop/03_search.py --photos
# your own photos, nothing leaves your laptop
uv run workshop/07_photo_search.py ~/Pictures
# a photo as the query
uv run workshop/08_image_search.py data/query_images/yerebatan.jpg
```

## How it works

```python
# text + vision, 440M
model = SentenceTransformer(
    "google/embeddinggemma-2", config_kwargs={"audio_config": None}
)

# no prompt for media
photo_vectors = model.encode([{"image": "data/images/galata-kulesi.jpg"}, ...])
query_vector = model.encode(
    "a stone tower by the sea", prompt_name="SearchQuery"
)
model.similarity(query_vector, photo_vectors)
```

Two rules:

1. **Media get no task prefix.** Only text does.
2. Inside text, `<|image|>`, `<|video|>` and `<|audio|>` are placeholders for media. If a document *talks about*
   these markers, escape them, or the processor will wait for an image that never comes
   (`nerede/prompts.py` does this for you).

## Search by photo { #by-photo }

A photo can be the query too. It goes through the vision encoder with no prompt, exactly like the indexed photos,
and its vector lands in the same space as everything else. So one query vector finds two things:

- **similar photos** (image → image): the indexed photo of the same place
- **matching places** (image → text): the place descriptions, in Turkish or English

```bash
uv run workshop/08_image_search.py data/query_images/kunefe.jpg
uv run workshop/08_image_search.py --eval   # 27 photos the model never saw
```

In the app, click the camera in the search bar, drop a photo anywhere on the page, or paste one (Ctrl+V).
The photo stays in the bar as a small chip until you remove it.

- **Browser** mode, including the [live demo](../../../demo/): the first photo downloads the vision encoder
  (about 109 MB with WebGPU), then the photo never leaves your device.
- **Server** mode: works when the server has PyTorch, which is the case for a local run. The LiteRT container is
  text only, so it hides the camera there.

### Photo plus words

Type words next to the photo and both go into one query: `normalize(photo + text)`. The words steer the photo.
The Galata Tower photo with a ferry in front returns the Bosphorus tour on its own, and Galata Kulesi with `kule`.
A glass of tea in front of the bridge returns tea on its own, and the Bosphorus Bridge with `bridge`.
Feeding photo and text to the model together (`"... <|image|>"`) gave about the same results, and adding the two
vectors is cheaper: the photo is embedded once, and changing the words only embeds the text again.

Each place has a photo and a text, so `Index.search_by_photo` lets both vote. Text scores run about 0.08 lower than
photo scores, so they are shifted onto the photo scale first, then the two are averaged:

```python
photo = place_photo_vectors @ q  # image -> image
text = place_text_vectors @ q  # image -> text
score = (photo + text + photo.mean() - text.mean()) / 2
```

The query photos in `data/query_images/` are other Wikimedia Commons photos of 27 indexed places, picked by hand,
so the model never saw them. Right place in the top 1 / top 3:

| dim | image → image | image → text | both |
|---|---|---|---|
| 768 | 0.63 / 0.78 | 0.48 / 0.70 | **0.74 / 0.85** |
| 512 | 0.59 / 0.74 | 0.52 / 0.67 | **0.74 / 0.85** |
| 256 | 0.56 / 0.78 | 0.41 / 0.63 | **0.67 / 0.81** |
| 128 | 0.56 / 0.74 | 0.37 / 0.56 | **0.63 / 0.85** |

The misses are worth a look. A Galata Tower photo with a ferry in front comes back as the Bosphorus tour, Rumeli
Hisarı swaps with its twin across the water, Anadolu Hisarı, and Turkish coffee lands next to tea. With 27 photos,
one photo moves a number by about 0.04, so treat the table as a rough guide.

## The photos

The 106 photos come from Wikimedia Commons under CC BY, CC BY-SA, Free Art License or public domain.
`scripts/data/fetch_images.py` takes the lead image of each place's Wikipedia article, checks the license and
writes the credits to `data/images/ATTRIBUTION.md`. The app shows the author and license under every photo.
The query photos come from `scripts/data/fetch_query_images.py`, with credits in `data/query_images/ATTRIBUTION.md`.

## Try it

- [ ] Turn on only the **Photos** filter and search `"street food"`. Which dishes come up?
- [ ] Search with a photo from your phone: a street, a dish, a ferry. Which place comes back first?
- [ ] Run `08_image_search.py --eval --dim 128` and compare the misses with 768d.
- [ ] Search with a Turkish phrase: `"deniz kenarında taş kule"`.
- [ ] Mix modalities: `model.encode({"text": "A day out <|image|>", "image": "photo.jpg"})` embeds a post with its photo as one vector.
