"""Nerede? API: semantic search over the prebuilt index, plus the web UI.

    uv run uvicorn app.main:app --reload                      # torch, local dev
    NEREDE_BACKEND=litert uv run uvicorn app.main:app         # what the container runs

Search by photo (POST /api/search/image) needs PyTorch for the vision encoder, so it works in local runs but not in
the LiteRT container. The encoder loads on the first photo query.
"""

import importlib.util
import io
import os
import threading
import time
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from PIL import Image

from nerede import Index, get_embedder, query
from nerede.index import DATA
from nerede.router import Router

index = Index.load()
embedder = get_embedder()
router = Router(embedder)
default_dim = int(os.environ.get("NEREDE_DIM", "768"))
photo_of = {img["id"]: img for img in index.images}
has_vision = importlib.util.find_spec("torch") is not None and len(index.images) > 0
_vision, _vision_lock = None, threading.Lock()
MAX_PHOTO_BYTES = 10 * 1024 * 1024


def vision():
    """The text + vision model (440M), loaded once, on the first photo query."""
    global _vision
    with _vision_lock:
        if _vision is None:
            from nerede.embedders import TorchEmbedder

            _vision = TorchEmbedder(modalities=("text", "image"))
    return _vision


app = FastAPI(title="Nerede?", description="Ask Istanbul anything, in Turkish or English.")

Text = Query(..., min_length=1, max_length=500)
Dim = Query(default_dim, ge=128, le=768)


@app.get("/api/health")
def health():
    collections = {}
    for d in index.docs:
        collections[d["collection"]] = collections.get(d["collection"], 0) + 1
    return {
        "ok": True,
        "backend": embedder.name,
        "index": index.built_with,
        "collections": collections,
        "photos": len(index.images),
        "vision": has_vision,
    }


@app.get("/api/search")
def search(
    q: str = Text,
    k: int = Query(6, ge=1, le=20),
    dim: int = Dim,
    collection: list[Literal["all", "places", "devfest", "devfest2025", "gemma"]] = Query(["all"]),
    mode: Literal["hybrid", "vector"] = "hybrid",
):
    """Repeat `collection` to search several (?collection=places&collection=gemma). Hybrid adds small intent and
    keyword boosts for one- or two-word queries; longer ones are pure vector search."""
    start = time.perf_counter()
    vector = embedder.embed([query(q)])[0]
    intent = router.route(q)
    hybrid = {"text": q, "intent": intent} if mode == "hybrid" else {}
    hits = index.search(vector, k=k, dim=dim, collection=collection, **hybrid)
    return {
        "query": q,
        "intent": intent[0],
        "mode": mode,
        "backend": embedder.name,
        "dim": dim,
        "ms": round((time.perf_counter() - start) * 1000, 1),
        "results": [{"score": round(score, 4), **doc, "photo": photo_of.get(doc["id"])} for score, doc in hits],
    }


@app.get("/api/photos")
def photos(q: str = Text, k: int = Query(12, ge=1, le=40), dim: int = Dim):
    """Text query against photo vectors: the 270M text model alone is enough at query time."""
    start = time.perf_counter()
    hits = index.search_images(embedder.embed([query(q)])[0], k=k, dim=dim)
    return {
        "query": q,
        "backend": embedder.name,
        "dim": dim,
        "ms": round((time.perf_counter() - start) * 1000, 1),
        "results": [{"score": round(score, 4), **img} for score, img in hits],
    }


@app.post("/api/search/image")
async def search_image(
    request: Request,
    k: int = Query(6, ge=1, le=20),
    dim: int = Dim,
    q: str | None = Query(None, max_length=500),
):
    """Search by photo. Send the image itself as the request body (JPEG, PNG or WebP, up to 10 MB). The photo is
    embedded with no prompt. Places are ranked by both their photo (image -> image) and their text (image -> text),
    which share one vector space; the photo strip is image -> image only. Add words with `q` ("kule", "at night"):
    the photo vector and the text vector are added into one query."""
    if not has_vision:
        raise HTTPException(501, "search by photo needs PyTorch (the LiteRT container is text only)")
    body = await request.body()
    if len(body) > MAX_PHOTO_BYTES:
        raise HTTPException(413, "photo is larger than 10 MB")
    try:
        image = Image.open(io.BytesIO(body)).convert("RGB")
    except Exception:
        raise HTTPException(400, "send a JPEG, PNG or WebP photo as the request body") from None
    image.thumbnail((1024, 1024))
    model = await run_in_threadpool(vision)
    start = time.perf_counter()
    vector = (await run_in_threadpool(model.embed_images, [image]))[0]
    if q:  # photo + words: one query vector, normalize(photo + text)
        text = (await run_in_threadpool(embedder.embed, [query(q)]))[0]
        vector = (vector + text) / np.linalg.norm(vector + text)
    places = index.search_by_photo(vector, k=k, dim=dim)
    photos = index.search_images(vector, k=12, dim=dim)
    return {
        "mode": "image",
        "backend": model.name,
        "dim": dim,
        "ms": round((time.perf_counter() - start) * 1000, 1),
        "results": [{"score": round(score, 4), **doc, "photo": photo_of.get(doc["id"])} for score, doc in places],
        "photos": [{"score": round(score, 4), **img} for score, img in photos],
    }


if (DATA / "images").exists():
    app.mount("/images", StaticFiles(directory=DATA / "images"), name="images")
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
