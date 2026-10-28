# 6. Ship it

## Run the app

```bash
NEREDE_BACKEND=litert uv run uvicorn app.main:app --reload
```

On Windows, set `NEREDE_BACKEND` as shown in [Setup](../setup.md#windows).

Open <http://127.0.0.1:8000>. The page has two modes:

- **Server**: the browser calls `/api/search` and `/api/photos`, and LiteRT embeds the query on the server.
- **Browser**: the page downloads the model (cached afterwards) and searches `index.json` locally.
  The question never leaves the device. With WebGPU it uses the 4-bit model (~175 MB). Without WebGPU it falls back
  to WASM with fp16 (~543 MB), because the 4-bit and 8-bit files need a kernel the WASM backend does not have.
  Add `?device=wasm` to the URL to try the fallback.

| Endpoint | Example |
|---|---|
| `GET /api/search` | `/api/search?q=balık ekmek&collection=places&dim=256&k=6`, repeat `collection` to search several |
| `GET /api/photos` | `/api/photos?q=domes and minarets&k=12` |
| `POST /api/search/image` | send a photo as the body: `curl --data-binary @photo.jpg -H 'Content-Type: image/jpeg' …/api/search/image?q=kule`, `q` is optional, needs PyTorch on the server |
| `GET /api/health` | backend, collection sizes, photo count |

The filter buttons combine: **All** turns everything on, any other button includes or excludes that collection, and
**Photos** adds a strip of matching photos. Links are shareable: `/?q=kaç kişi geldi&only=devfest,devfest2025`.

## Build a container

```bash
docker build -t nerede .        # or: podman build -t nerede .
docker run -p 8080:8080 nerede  # http://127.0.0.1:8080
```

The image contains FastAPI, LiteRT and the 165 MB model, but no PyTorch.
It is about 575 MB, starts in about a second and uses about 200 MB of RAM.

## Publish it for free

=== "GitHub Pages (static)"

    The page falls back to browser mode when there is no API, so the demo can be plain files:

    ```bash
    uv run --group docs scripts/docs/build_docs.py --with-demo
    ```

    `site/` then contains these docs (English and Turkish) and the demo under `demo/`.
    `.github/workflows/docs.yml` publishes it on every push to `main`.

=== "Hugging Face Spaces (server)"

    Create a **Docker** Space (free CPU), push this repository and add to the Space README:

    ```yaml
    sdk: docker
    app_port: 8080
    ```

=== "Cloud Run"

    [![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run/?git_repo=https://github.com/onuralpszr/nerede.git&revision=main)

    The button opens Cloud Shell, builds the `Dockerfile` and deploys it. `app.json` asks for 1 GiB of memory and
    at most 2 instances, so a forgotten demo stays cheap. Cloud Run needs a billing account, and its free tier
    covers a small demo. The container is the LiteRT one, so it searches text and hides the photo camera.
