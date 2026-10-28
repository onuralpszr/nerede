# scripts

Helpers that build things around the workshop. None of them are needed to follow the workshop itself.
Run them from the repository root.

| Folder | Script | What it does |
|---|---|---|
| `draw/` | `make_skyline.py` | draws the pixel-art Istanbul skyline (SVG) for the app and the docs |
| `data/` | `fetch_images.py` | downloads place photos from Wikimedia Commons, with license and credits |
| `docs/` | `build_docs.py` | builds the English and Turkish docs, optionally with the browser demo |
| `notebooks/` | `make_notebooks.py` | writes the Colab and Kaggle notebooks in `notebooks/` |

```bash
uv run scripts/draw/make_skyline.py
uv run scripts/data/fetch_images.py
uv run --group docs scripts/docs/build_docs.py --with-demo --serve
uv run --group dev scripts/notebooks/make_notebooks.py
```
