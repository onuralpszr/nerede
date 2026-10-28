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

## Try it

- [ ] Add a `sports` category. Which questions move to it?
- [ ] Write the descriptions in Turkish only. Does English still route correctly?
