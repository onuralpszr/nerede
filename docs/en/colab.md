# Colab notebook

Two notebooks contain the complete workshop, one per language. They run on the **free** Colab tier.

| Notebook | Open |
|---|---|
| English | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/onuralpszr/nerede/blob/main/notebooks/nerede_en.ipynb) |
| Türkçe | [![Colab'da aç](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/onuralpszr/nerede/blob/main/notebooks/nerede_tr.ipynb) |

## What the notebook does

1. **Setup**: clones the repository and installs `sentence-transformers`, `litert-lm-api` and the app (Colab already has PyTorch).
2. **Hello embeddings**: task prompts and Turkish ↔ English similarity.
3. **Build the index**: places, DevFest facts, EmbeddingGemma notes and photos.
4. **Search**: text search and text → photo search, shown with the images inline.
5. **Measure**: recall at 768, 512, 256 and 128 dimensions.
6. **Router**: zero-shot intent classification.
7. **LiteRT**: the same queries through the 165 MB on-device model, compared with PyTorch.
8. **Web app**: starts the FastAPI server inside Colab and prints a link to the UI.

## Tips for the free tier

- **Runtime → Change runtime type → T4 GPU** speeds up photo indexing. The notebook falls back to CPU automatically.
- If Colab disconnects, run **Runtime → Run all** again. The models are cached for the session.
- The web app link only works while the notebook is running.

## Running it locally

The notebooks also run in Jupyter or VS Code on your own machine:

```bash
uv run --with jupyterlab jupyter lab notebooks/
```
