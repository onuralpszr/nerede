# EmbeddingGemma 2 in one page

An open, multimodal embedding model from Google DeepMind, built on Gemma 4 and released under **Apache 2.0**.
It maps **text (including code), images, audio and video** into one shared 768-dimensional space.

## Sizes

| Part | Parameters | Load it with |
|---|---|---|
| Text model (transformer 130M + embedding table 140M) | 270M | `vision_config=None, audio_config=None` |
| + vision encoder | +170M (440M) | `audio_config=None` |
| + audio encoder | +300M (570M) | `vision_config=None` |
| Everything | 740M | default |

One checkpoint, one vector space: a text-only app and a full multimodal app produce compatible vectors.

## Key numbers

| | |
|---|---|
| Output | 768d, Matryoshka 512 / 256 / 128 |
| Context | 8,192 tokens, shared by all modalities (4x EmbeddingGemma 1) |
| Image | 280 tokens by default (70 to 1120), about 29 images per input |
| Video | 1 frame per second, 140 tokens per frame, up to 32 frames |
| Audio | 16 kHz mono, 25 tokens per second, about 5.5 minutes |
| Languages | 100+ |

## Benchmarks (768d, from the model card)

| Benchmark | EmbeddingGemma 2 | EmbeddingGemma 1 |
|---|---|---|
| MTEB multilingual v2 | 61.36 | 61.15 |
| MTEB code v1 | **78.68** | 68.76 |
| MIEB lite (images) | 64.64 | n/a |
| MMEB v2 video, Hit@1 | 50.67 | n/a |
| MSEB retrieval (audio), MRR@10 | 69.54 | n/a |

Truncation (MTEB multilingual): 768d 61.36 · 512d 61.17 · 256d 60.41 · 128d 57.89.

## Prompts

| Task | Query side | Document side |
|---|---|---|
| Search | `task: search result \| query: …` | `title: {title or none} \| text: …` |
| Question answering | `task: question answering \| query: …` | same |
| Fact checking | `task: fact checking \| query: …` | same |
| Code search | `task: code retrieval \| query: …` | `title: {file} \| text: {code}` |
| Classification | `task: classification \| query: …` | same prefix on both sides |
| Clustering | `task: clustering \| query: …` | same prefix on both sides |
| Similarity | `task: sentence similarity \| query: …` | same prefix on both sides |

Media (images, audio, video) get **no** prefix.

## Where it runs

| Runtime | Model id | Notes |
|---|---|---|
| sentence-transformers ≥ 6.1 | `google/embeddinggemma-2` | Python, any device |
| LiteRT-LM | `litert-community/embeddinggemma-2-text-270m-litert-lm` | int4 QAT, 165 MB; text+vision 388 MB; full 485 MB |
| transformers.js | `onnx-community/embeddinggemma-2-ONNX` | WebGPU/WASM, q4 text ~175 MB |
| Ollama | `embeddinggemma-2` | |
| llama.cpp | `ggml-org/embeddinggemma-2-GGUF` | |
| MLX | `mlx-community/embeddinggemma-2-*` | Apple Silicon |
| vLLM, SGLang, LM Studio, MediaPipe | | |

On-device latency for a text query (LiteRT-LM, from the model card): Pixel 11 Pro TPU 8.3 ms,
MacBook Pro M5 GPU 9.5 ms, iPhone 18 Pro GPU 11.6 ms, Raspberry Pi 5 CPU 161 ms.

## Sources

- [Model card on Hugging Face](https://huggingface.co/google/embeddinggemma-2)
- [Announcement](https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/) and [developer guide](https://developers.googleblog.com/embeddinggemma-2-the-developer-guide/)
- [Google AI Edge and LiteRT](https://developers.googleblog.com/google-ai-edge-with-embeddinggemma-2)
- [Fine-tuning guide](https://ai.google.dev/gemma/docs/embeddinggemma/fine-tuning-embeddinggemma-with-sentence-transformers) · [Unsloth](https://unsloth.ai/docs/models/embeddinggemma-2)

!!! tip
    The demo app has an **EmbeddingGemma** filter: everything on this page is also searchable there, in Turkish and English.
