# Dataset

All data lives in `data/` as JSON Lines: one record per line, easy to read, diff and extend.

| File | Records | What |
|---|---|---|
| `istanbul.jsonl` | 107 | places, food, transport and tips (55 Turkish, 52 English) |
| `devfest.jsonl` | 16 | DevFest İstanbul 2026 and GDG İstanbul (8 TR, 8 EN) |
| `embeddinggemma.jsonl` | 24 | notes about the model (12 TR, 12 EN) |
| `images.jsonl` + `images/` | 106 | one photo for almost every place, with author and license |
| `eval_queries.jsonl` | 72 | questions with the id of the right answer |

## A place

```json
{"id": "galata-kulesi", "title": "Galata Kulesi", "district": "Beyoğlu", "category": "view", "lang": "tr",
 "text": "1348'de Cenevizliler tarafından inşa edilen taş kule, Haliç ve tarihi yarımadanın en iyi panoramik manzaralarından birini sunar. Gün batımında seyir terasında sıra oluşabilir.",
 "source": "https://tr.wikipedia.org/wiki/Galata_Kulesi", "wiki_en": "Galata Tower", "wiki_tr": "Galata Kulesi",
 "lat": 41.02555556, "lon": 28.97416667}
```

Each document is written in **one** language on purpose. A Turkish question has to find English documents and the
other way round, which is exactly what a multilingual embedding model is for.

## How it was checked

- **Places**: every entry cites the Wikipedia article it was checked against (`source`). The first 51 entries
  were fact-checked against English and Turkish Wikipedia: 13 were corrected (for example, Ayasofya served as a
  museum from 1935, not 1934, and the archipelago of Adalar has nine islands, not four). 50 entries were then
  written directly from Wikipedia. The 16 practical tips that Wikipedia does not cover (like drinking pickle juice with
  balık ekmek) were checked a second time against official sites and travel guides: 11 were confirmed and 5 reworded
  (for example, the Bosphorus ferry is no longer called "the cheapest way" to see the city). Both rounds, with every
  source, are in `data/drafts/factcheck_report.md` and `data/drafts/factcheck_round2.md`.
- **DevFest**: only facts from [devfest.istanbul](https://devfest.istanbul/) and its archive, plus a Webrazzi article
  for the 2025 date. Dates, venue and ticket prices were re-checked on 28 October 2026 against the site and Kommunity; prices may change.
- **EmbeddingGemma**: only facts from the model cards and Google's announcement posts.

!!! warning "Please double-check before quoting"
    The data was prepared for a workshop demo. If you spot a mistake, fix the line and rebuild the index.

## Photos and licenses

`scripts/fetch_images.py` downloads the lead image of each place's Wikipedia article from Wikimedia Commons and keeps
it only if the license is CC0, CC BY, CC BY-SA, Free Art License or public domain. Two logos were replaced with
real photos. Every photo's author, license and source page is in `data/images.jsonl` and
`data/images/ATTRIBUTION.md`, and the app shows the credit under each photo.

## Add your own

1. Add a line to `data/istanbul.jsonl` (or any collection) with a unique `id`.
2. Optionally add a photo: put `data/images/<id>.jpg` in place and a line in `data/images.jsonl`.
3. `uv run workshop/02_build_index.py` and search for it.
