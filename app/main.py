"""Nerede? API: semantic search over the prebuilt index, plus the web UI.

    uv run uvicorn app.main:app --reload                      # torch, local dev
    NEREDE_BACKEND=litert uv run uvicorn app.main:app         # what the container runs
"""

import os
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

from nerede import Index, get_embedder, query
from nerede.index import DATA
from nerede.router import Router

index = Index.load()
embedder = get_embedder()
router = Router(embedder)
default_dim = int(os.environ.get("NEREDE_DIM", "768"))
photo_of = {img["id"]: img for img in index.images}

app = FastAPI(title="Nerede?", description="Ask Istanbul anything, in Turkish or English.")

Text = Query(..., min_length=1, max_length=500)
Dim = Query(default_dim, ge=128, le=768)


@app.get("/api/health")
def health():
    collections = {}
    for d in index.docs:
        collections[d["collection"]] = collections.get(d["collection"], 0) + 1
    return {"ok": True, "backend": embedder.name, "index": index.built_with,
            "collections": collections, "photos": len(index.images)}


@app.get("/api/search")
def search(q: str = Text, k: int = Query(6, ge=1, le=20), dim: int = Dim,
           collection: Literal["all", "places", "devfest", "gemma"] = "all",
           mode: Literal["hybrid", "vector"] = "hybrid"):
    """Hybrid adds small intent and keyword boosts for one- or two-word queries; longer ones are pure vector search."""
    start = time.perf_counter()
    vector = embedder.embed([query(q)])[0]
    intent = router.route(q)
    hybrid = {"text": q, "intent": intent} if mode == "hybrid" else {}
    hits = index.search(vector, k=k, dim=dim, collection=collection, **hybrid)
    return {"query": q, "intent": intent[0], "mode": mode, "backend": embedder.name, "dim": dim,
            "ms": round((time.perf_counter() - start) * 1000, 1),
            "results": [{"score": round(score, 4), **doc, "photo": photo_of.get(doc["id"])} for score, doc in hits]}


@app.get("/api/photos")
def photos(q: str = Text, k: int = Query(12, ge=1, le=40), dim: int = Dim):
    """Text query against photo vectors: the 270M text model alone is enough at query time."""
    start = time.perf_counter()
    hits = index.search_images(embedder.embed([query(q)])[0], k=k, dim=dim)
    return {"query": q, "backend": embedder.name, "dim": dim,
            "ms": round((time.perf_counter() - start) * 1000, 1),
            "results": [{"score": round(score, 4), **img} for score, img in hits]}


if (DATA / "images").exists():
    app.mount("/images", StaticFiles(directory=DATA / "images"), name="images")
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
