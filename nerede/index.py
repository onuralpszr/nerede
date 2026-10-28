"""A tiny vector index: numpy matrices plus the records. Enough for thousands of docs and photos."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from nerede.keywords import Keywords, keyword_text, tokens
from nerede.prompts import document

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PLACES = DATA / "istanbul.jsonl"
INDEX = ROOT / "index" / "istanbul.npz"

# collection name -> file. Places are the Istanbul guide, the other two are small knowledge bases.
COLLECTIONS = {
    "places": DATA / "istanbul.jsonl",
    "devfest": DATA / "devfest.jsonl",
    "gemma": DATA / "embeddinggemma.jsonl",
}
IMAGES = DATA / "images.jsonl"

# Hybrid search for short queries. A query of one or two words ("tatlı", "müze") carries little meaning, so every
# food entry scores about the same. Two small boosts fix that, tuned on data/eval_short.jsonl (step 3):
# the Router's intent, when it is confident, and keyword (BM25) matches. Longer queries keep the plain vector score.
SHORT_QUERY_WORDS = 2
INTENT_BOOST, INTENT_MIN_CONFIDENCE = 0.05, 0.79
KEYWORD_BOOST = 0.03


def read_jsonl(path: Path | str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def load_places(path: Path | str = PLACES) -> list[dict]:
    return read_jsonl(path)


def load_corpus(collections: list[str] | None = None) -> list[dict]:
    """All documents, each tagged with its collection."""
    docs = []
    for name, path in COLLECTIONS.items():
        if collections and name not in collections:
            continue
        docs += [{**d, "collection": d.get("collection", name)} for d in read_jsonl(path)]
    return docs


def load_images() -> list[dict]:
    """Photo records (one per place that has a freely licensed Wikimedia Commons photo)."""
    if not IMAGES.exists():
        return []
    return [i for i in read_jsonl(IMAGES) if (DATA / "images" / i["file"]).exists()]


def in_intent(doc: dict, label: str) -> bool:
    """Router labels are place categories, plus "devfest" and "ai" for the two knowledge bases."""
    if label in ("devfest", "ai"):
        return doc["collection"] == ("gemma" if label == "ai" else "devfest")
    return doc["collection"] == "places" and doc.get("category") == label


def truncate(vectors: np.ndarray, dim: int) -> np.ndarray:
    """Matryoshka: keep the first `dim` values, then re-normalize (skipping this silently hurts ranking)."""
    v = vectors[..., :dim]
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


@dataclass
class Index:
    docs: list[dict]
    vectors: np.ndarray  # (n, 768) float32, L2-normalized
    built_with: str = "unknown"
    images: list[dict] = field(default_factory=list)
    image_vectors: np.ndarray = field(default_factory=lambda: np.zeros((0, 768), np.float32))
    _keywords: Keywords | None = field(default=None, init=False, repr=False)

    @classmethod
    def build(cls, embedder, docs: list[dict]) -> Index:
        texts = [document(d["text"], title=d["title"]) for d in docs]
        return cls(docs, embedder.embed(texts), built_with=embedder.name)

    def add_images(self, image_embedder, images: list[dict]) -> None:
        """Images get no prompt. Their vectors live in the same space as the text vectors."""
        self.images = images
        self.image_vectors = image_embedder.embed_images([str(DATA / "images" / i["file"]) for i in images])

    def search(self, query_vector: np.ndarray, k: int = 5, dim: int = 768, collection: str | None = None,
               text: str | None = None, intent: tuple[str, float] | None = None) -> list[tuple[float, dict]]:
        """Cosine search. Pass the query `text` (and the Router's `intent`) to turn on hybrid boosts for short queries."""
        keep = np.array([collection in (None, "all", d["collection"]) for d in self.docs])
        scores = truncate(self.vectors, dim) @ truncate(query_vector, dim)
        if text is not None:
            scores = scores + self.boosts(text, intent)
        scores[~keep] = -np.inf
        order = np.argsort(-scores)[: min(k, int(keep.sum()))]
        return [(float(scores[i]), self.docs[i]) for i in order]

    def boosts(self, text: str, intent: tuple[str, float] | None = None) -> np.ndarray:
        out = np.zeros(len(self.docs), np.float32)
        if len(tokens(text)) > SHORT_QUERY_WORDS:
            return out
        if intent and intent[1] >= INTENT_MIN_CONFIDENCE:
            out += INTENT_BOOST * np.array([in_intent(d, intent[0]) for d in self.docs], np.float32)
        if self._keywords is None:
            self._keywords = Keywords([keyword_text(d) for d in self.docs])
        hits = self._keywords.scores(text)
        if hits.max() > 0:
            out += KEYWORD_BOOST * hits / hits.max()
        return out

    def search_images(self, query_vector: np.ndarray, k: int = 8, dim: int = 768) -> list[tuple[float, dict]]:
        if not len(self.images):
            return []
        scores = truncate(self.image_vectors, dim) @ truncate(query_vector, dim)
        return [(float(scores[i]), self.images[i]) for i in np.argsort(-scores)[:k]]

    @property
    def places(self) -> list[dict]:
        return [d for d in self.docs if d["collection"] == "places"]

    def save(self, path: Path | str = INDEX) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, vectors=self.vectors, docs=json.dumps(self.docs, ensure_ascii=False),
                            built_with=self.built_with, image_vectors=self.image_vectors,
                            images=json.dumps(self.images, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path | str = INDEX) -> Index:
        data = np.load(path)
        return cls(json.loads(str(data["docs"])), data["vectors"], str(data["built_with"]),
                   json.loads(str(data["images"])), data["image_vectors"])

    def export_web(self, path: Path | str, dim: int = 256, router=None) -> None:
        """Write a small JSON the browser can search: the page only has to embed the query.
        With a Router, its label vectors go along (full 768d) so Browser mode can do hybrid search too."""
        def pack(v, d=dim):
            return np.round(truncate(v, d), 4).tolist() if len(v) else []

        payload = {"model": "google/embeddinggemma-2", "dim": dim, "built_with": self.built_with,
                   "docs": self.docs, "vectors": pack(self.vectors),
                   "images": self.images, "image_vectors": pack(self.image_vectors)}
        if router is not None:
            payload["hybrid"] = {"labels": router.labels, "label_vectors": pack(router.vectors, 768),
                                 "short_query_words": SHORT_QUERY_WORDS, "intent_boost": INTENT_BOOST,
                                 "intent_min_confidence": INTENT_MIN_CONFIDENCE, "keyword_boost": KEYWORD_BOOST}
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
