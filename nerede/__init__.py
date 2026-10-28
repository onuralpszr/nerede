"""Nerede? Multilingual semantic search for Istanbul, powered by EmbeddingGemma 2."""

from nerede.embedders import get_embedder
from nerede.index import Index, load_corpus, load_images, load_places
from nerede.prompts import document, query

__all__ = ["Index", "document", "get_embedder", "load_corpus", "load_images", "load_places", "query"]
