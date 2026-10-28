"""EmbeddingGemma 2 task prefixes, straight from the model card.

Text only: images, audio and video are embedded without any prefix.
Retrieval is asymmetric (query prefix vs document prefix); classification,
clustering and similarity are symmetric (same prefix on both sides).
"""

import re

# <|image|>, <|video|> and <|audio|> are media placeholders. Inside plain text they must be
# defused, or a model with the vision/audio encoder loaded expects media that never comes.
_MEDIA_TOKEN = re.compile(r"<\|(image|video|audio)\|>")


def _plain(text: str) -> str:
    return _MEDIA_TOKEN.sub(r"<\1>", text.strip())


def query(text: str, task: str = "search result") -> str:
    return f"task: {task} | query: {_plain(text)}"


def document(text: str, title: str = "none") -> str:
    return f"title: {_plain(title)} | text: {_plain(text)}"


def classification(text: str) -> str:
    return query(text, task="classification")
