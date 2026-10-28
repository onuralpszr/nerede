"""Step 1: what is an embedding? Prompts, similarity and cross-lingual search in ~20 lines."""

from sentence_transformers import SentenceTransformer

from nerede.embedders import pick_torch_device

# Text-only: skip the vision and audio encoders -> 270M parameters instead of 740M.
model = SentenceTransformer(
    "google/embeddinggemma-2",
    device=pick_torch_device(),
    config_kwargs={"vision_config": None, "audio_config": None},
)

documents = [
    "Kız Kulesi, Üsküdar açıklarında küçük bir adacık üzerinde yer alan tarihi bir kuledir.",
    "The Grand Bazaar is one of the largest and oldest covered markets in the world.",
    "Balık ekmek, Eminönü'nde teknelerden satılan ızgara balık sandviçidir.",
]
queries = [
    "a tower on a tiny island",  # EN query -> TR document
    "where can I eat a fish sandwich?",  # EN query -> TR document
    "eski kapalı çarşı",  # TR query -> EN document
]

# Retrieval is asymmetric: queries and documents get different task prompts.
print("prompts:", model.prompts["SearchQuery"], "/", model.prompts["Document"])
doc_emb = model.encode(documents, prompt_name="Document")
query_emb = model.encode(queries, prompt_name="SearchQuery")
print("shape:", doc_emb.shape)

scores = model.similarity(query_emb, doc_emb)
for q, row in zip(queries, scores, strict=True):
    best = int(row.argmax())
    print(f"\n{q!r}\n  -> {documents[best][:70]}...  ({row[best]:.3f})")

# Try it: remove prompt_name from both encode() calls. Do the scores get worse?
