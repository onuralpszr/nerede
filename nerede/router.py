"""Zero-shot intent routing: embed category descriptions once, pick the closest one per query.

The same idea powers MediaPipe's Decision Task: no training, just labels in the vector space.
"""

from __future__ import annotations

import numpy as np

from nerede.prompts import classification

CATEGORIES = {
    "food": "food, eating, restaurants, street food, breakfast, coffee, dessert / yemek, kahvaltı, tatlı",
    "history": "history, mosques, churches, Byzantine and Ottoman monuments / tarih, cami, saray",
    "museum": "museums, art galleries, exhibitions / müze, sanat, sergi",
    "view": "viewpoints, panoramic views, sunset, towers / manzara, gün batımı, seyir terası",
    "nature": "parks, forests, islands, gardens, running / park, orman, ada, doğa",
    "transport": "transport, ferry, metro, tram, travel card / ulaşım, vapur, metro, tramvay",
    "shopping": "shopping, bazaars, markets, antiques, books / alışveriş, çarşı, antika",
    "neighborhood": "neighborhoods to walk around, streets, districts / semt, mahalle, sokak",
    "nightlife": "nightlife, bars, drinks, evening out / gece hayatı, meyhane, bar",
    "experience": "local experiences, tips, hamam, cats, rainy day / deneyim, ipucu, hamam",
    "devfest": "DevFest conference, tickets, venue, speakers, sessions, GDG community / konferans, bilet, etkinlik",
    "ai": "the AI model: EmbeddingGemma, parameters, supported languages, vector dimensions, benchmarks, runtimes, "
    "prompts / yapay zeka modeli, kaç dil, parametre, vektör boyutu",
}


class Router:
    def __init__(self, embedder):
        self.embedder = embedder
        self.labels = list(CATEGORIES)
        self.vectors = embedder.embed([classification(d) for d in CATEGORIES.values()])

    def route(self, text: str) -> tuple[str, float]:
        scores = self.vectors @ self.embedder.embed([classification(text)])[0]
        best = int(np.argmax(scores))
        return self.labels[best], float(scores[best])
