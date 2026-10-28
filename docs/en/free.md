# Free options

Every part of this workshop runs **without paying anything and without a credit card**.
Pick whatever matches your situation.

| You have | Use | Cost | What works |
|---|---|---|---|
| Any laptop (even without a GPU) | local, CPU PyTorch | free | everything |
| Only a browser | [Google Colab](colab.md) free tier | free | everything, including the web app via a Colab proxy link |
| A Kaggle account | Kaggle Notebooks | free | everything in the notebook |
| A phone or tablet | the hosted [browser demo](#demo) | free | search, in your browser |
| Something to share | GitHub Pages or a Hugging Face Space | free | public demo |

## Local CPU is enough

The text model has 270M parameters. On a laptop CPU it embeds a query in about 20 to 40 ms and indexes
the whole dataset in seconds. The photos (vision encoder, 440M) take about four minutes once, or you can use the prebuilt index.
You need about 3 GB of disk and 4 GB of free RAM.

## Google Colab (free)

Open the notebook from the [Colab page](colab.md). The free tier gives you a CPU runtime or a T4 GPU, which is plenty.
The notebook installs everything, builds the index, runs every step and finally starts the web app
inside Colab with a link you can open in a new tab.

!!! tip
    Choose **Runtime → Change runtime type → T4 GPU** for faster photo indexing. The rest is fast on CPU too.

## Kaggle Notebooks (free)

Kaggle gives about 30 GPU hours per week after phone verification. Upload `notebooks/nerede_en.ipynb`
(or the Turkish one), turn **Internet** on in the settings, and run all cells. The Colab-only cell that opens the web app is skipped automatically.

## Host the demo for free { #demo }

The web app has a **browser-only mode**: when it cannot reach the API, it downloads the model into the
browser and searches `index.json` locally. So the whole demo is just static files:

```bash
uv run --group docs scripts/docs/build_docs.py --with-demo      # site/ = docs (EN + TR) + demo/
```

Publish `site/` on **GitHub Pages** (the workflow in `.github/workflows/docs.yml` does it on every push)
and the demo lives at [onuralpszr.github.io/nerede/demo](https://onuralpszr.github.io/nerede/demo/). No server, no bill.

## Hugging Face Spaces (free CPU)

For the server version (LiteRT API + UI), create a **Docker** Space on the free CPU hardware, push this
repository, and add this to the Space README front matter:

```yaml
sdk: docker
app_port: 8080
```

The image is about 575 MB, starts in about a second and uses about 200 MB of RAM, well inside the free tier.

!!! note "Cloud Run"
    Google Cloud Run also has a free tier, but it needs a billing account. We will cover it separately.
