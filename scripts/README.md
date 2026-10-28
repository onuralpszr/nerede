# scripts

Helpers that build things around the workshop. None of them are needed to follow the workshop itself.
Run them from the repository root.

| Folder | Script | What it does |
|---|---|---|
| `draw/` | `make_skyline.py` | draws the pixel-art Istanbul skyline (SVG) for the app and the docs |
| `data/` | `fetch_images.py` | downloads place photos from Wikimedia Commons, with license and credits |
| `data/` | `fetch_query_images.py` | downloads a second photo of some places, used as image-search queries |
| `docs/` | `build_docs.py` | builds the English and Turkish docs, optionally with the browser demo |

```bash
uv run scripts/draw/make_skyline.py
uv run scripts/data/fetch_images.py
uv run scripts/data/fetch_query_images.py
uv run --group docs scripts/docs/build_docs.py --with-demo --serve
```
