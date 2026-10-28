"""Keyword scores (BM25) for hybrid search.

Embeddings match meaning, but a one-word query like "tatlı" carries little meaning and every food entry scores
about the same. Keywords fix that case: a document that literally says "tatlı" should win. The matching is
forgiving on purpose, because Turkish adds suffixes and people type without Turkish letters:

    fold("Künefe'yi")  -> "kunefe'yi"      Turkish İ/ı handled, accents folded: "kunefe" finds "Künefe"
    "tatli" matches "tatlisi", "tatlilar"   a query word of 4+ letters also matches longer words that start with it

app.js has the same code for Browser mode, keep the two in sync.
"""

from __future__ import annotations

import math
import re
import unicodedata

import numpy as np

STOPWORDS = set("""
a an and are at be by can do for from how i in is it me my of on or the to what when where which who with you your
bir bu da de en gibi hangi icin ile mi mu ne nasil nerede neden olan siz sen ve veya ya
""".split())


def fold(text: str) -> str:
    """Lowercase with Turkish rules, then drop accents: "İstanbul Çarşısı" -> "istanbul carsisi"."""
    text = text.replace("İ", "i").replace("I", "ı").lower().replace("ı", "i")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", fold(text)) if len(t) > 1 and t not in STOPWORDS]


def _matches(query_token: str, word: str) -> bool:
    return word == query_token or (len(query_token) >= 4 and word.startswith(query_token))


class Keywords:
    """BM25 over a list of texts. Small and exact: fine for thousands of documents."""

    def __init__(self, texts: list[str], k1: float = 1.2, b: float = 0.75):
        self.docs = [tokens(t) for t in texts]
        self.avg_len = sum(map(len, self.docs)) / max(1, len(self.docs))
        self.k1, self.b = k1, b

    def scores(self, text: str) -> np.ndarray:
        out = np.zeros(len(self.docs), np.float32)
        n = len(self.docs)
        for q in set(tokens(text)):
            tf = np.array([sum(_matches(q, w) for w in doc) for doc in self.docs], np.float32)
            df = int((tf > 0).sum())
            if not df:
                continue
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            lengths = np.array([len(doc) for doc in self.docs], np.float32)
            out += idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * lengths / self.avg_len))
        return out


def keyword_text(record: dict) -> str:
    """What the keyword side sees: title, district and text (photos only have a title)."""
    district = record.get("district")
    return " ".join([record.get("title", ""), district if district and district != "Everywhere" else "",
                     record.get("text", "")])
