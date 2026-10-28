# 4. Zero-shot router

Classification without training data: describe each category in a sentence, embed the descriptions once,
and assign each question to the closest one.

```bash
uv run workshop/05_router.py
```

```text
   nightlife  0.866  akşam rakı içmek için güzel bir yer
   transport  0.784  how do I pay for the metro?
      museum  0.847  çocuklarla gidilecek müze
     devfest  0.868  DevFest bileti ne kadar?
          ai  0.807  how many dimensions does the embedding have
```

Classification is a **symmetric** task, so the same prefix goes on both sides:

```python
CATEGORIES = {
    "food": "food, eating, restaurants, street food, breakfast / yemek, kahvaltı, tatlı",
    "devfest": "DevFest conference, tickets, venue, speakers / konferans, bilet, etkinlik",
    ...
}
labels = embedder.embed([classification(d) for d in CATEGORIES.values()])   # once
scores = labels @ embedder.embed([classification(question)])[0]             # per question
```

The web app uses this to show an **intent** badge next to every answer. MediaPipe's Decision Task
packages the same idea for Android, iOS and the web.

## Router + keywords = hybrid search { #hybrid }

A one-word query like "tatlı" or "müze" carries little meaning: every food entry scores about the same, and
simit can beat baklava. The router helps here. For queries of **one or two words**, `Index.search` adds two
small boosts on top of the cosine score:

- **intent**: +0.05 for entries in the category the router picks, but only when it is confident (score 0.79 or more);
- **keywords**: up to +0.03 from BM25 over title and text. Turkish-aware: "tatli" finds "tatlı" and "tatlısı".

```python
hits = index.search(vector, k=5, text=q, intent=router.route(q))   # hybrid
hits = index.search(vector, k=5)                                   # plain vector search
```

Longer queries keep the plain vector score, so the 72 sentence questions score exactly the same. Step 3 measures
the one-word case on `data/eval_short.jsonl` (24 queries, how many of the top 5 are relevant):

| | vector | hybrid |
|---|---|---|
| LiteRT queries, 768d | 0.68 | **0.86** |
| LiteRT queries, 256d | 0.64 | **0.83** |

The server and Browser mode both use it; add `?search=vector` to the page URL (or `mode=vector` to the API) to compare.
Turning the boost on for every query lowered recall@1 on the sentence questions, and the router is not sure about
some single words ("cami" goes to `ai` with 0.77), which is why both limits exist.

## Try it

- [ ] Add a `sports` category. Which questions move to it?
- [ ] Write the descriptions in Turkish only. Does English still route correctly?
- [ ] Change `INTENT_BOOST` or `KEYWORD_BOOST` in `nerede/index.py` and run step 3 again. Where does it start to hurt?
