# Tek sayfada EmbeddingGemma 2

Google DeepMind'ın Gemma 4 üzerine kurduğu, **Apache 2.0** lisanslı, açık ve çok modlu embedding modeli.
**Metni (kod dahil), görselleri, sesi ve videoyu** tek bir ortak 768 boyutlu uzaya yerleştirir.

## Boyutlar

| Parça | Parametre | Nasıl yüklenir |
|---|---|---|
| Metin modeli (transformer 130M + embedding tablosu 140M) | 270M | `vision_config=None, audio_config=None` |
| + görsel kodlayıcı | +170M (440M) | `audio_config=None` |
| + ses kodlayıcı | +300M (570M) | `vision_config=None` |
| Hepsi | 740M | varsayılan |

Tek checkpoint, tek vektör uzayı: yalnızca metin kullanan bir uygulama ile tam çok modlu bir uygulama birbiriyle uyumlu vektörler üretir.

## Temel sayılar

| | |
|---|---|
| Çıktı | 768 boyut, Matryoshka ile 512 / 256 / 128 |
| Bağlam | 8.192 token, tüm modaliteler paylaşır (EmbeddingGemma 1'in 4 katı) |
| Görsel | varsayılan 280 token (70 ile 1120 arası), bir girdiye yaklaşık 29 görsel |
| Video | saniyede 1 kare, kare başına 140 token, en çok 32 kare |
| Ses | 16 kHz mono, saniyede 25 token, yaklaşık 5,5 dakika |
| Diller | 100'den fazla |

## Benchmark sonuçları (768 boyut, model kartından)

| Benchmark | EmbeddingGemma 2 | EmbeddingGemma 1 |
|---|---|---|
| MTEB çok dilli v2 | 61,36 | 61,15 |
| MTEB kod v1 | **78,68** | 68,76 |
| MIEB lite (görsel) | 64,64 | yok |
| MMEB v2 video, Hit@1 | 50,67 | yok |
| MSEB erişim (ses), MRR@10 | 69,54 | yok |

Kesme (MTEB çok dilli): 768 boyut 61,36 · 512 boyut 61,17 · 256 boyut 60,41 · 128 boyut 57,89.

## Önekler

| Görev | Sorgu tarafı | Belge tarafı |
|---|---|---|
| Arama | `task: search result \| query: …` | `title: {başlık ya da none} \| text: …` |
| Soru cevaplama | `task: question answering \| query: …` | aynı |
| Doğruluk kontrolü | `task: fact checking \| query: …` | aynı |
| Kod arama | `task: code retrieval \| query: …` | `title: {dosya} \| text: {kod}` |
| Sınıflandırma | `task: classification \| query: …` | iki tarafta aynı önek |
| Kümeleme | `task: clustering \| query: …` | iki tarafta aynı önek |
| Benzerlik | `task: sentence similarity \| query: …` | iki tarafta aynı önek |

Medya (görsel, ses, video) **önek almaz**.

## Nerede çalışır

| Runtime | Model kimliği | Not |
|---|---|---|
| sentence-transformers ≥ 6.1 | `google/embeddinggemma-2` | Python, her cihaz |
| LiteRT-LM | `litert-community/embeddinggemma-2-text-270m-litert-lm` | int4 QAT, 165 MB, metin+görsel 388 MB, tam model 485 MB |
| transformers.js | `onnx-community/embeddinggemma-2-ONNX` | WebGPU/WASM, q4 metin ~175 MB |
| Ollama | `embeddinggemma-2` | |
| llama.cpp | `ggml-org/embeddinggemma-2-GGUF` | |
| MLX | `mlx-community/embeddinggemma-2-*` | Apple Silicon |
| vLLM, SGLang, LM Studio, MediaPipe | | |

Cihaz üzerinde bir metin sorgusunun gecikmesi (LiteRT-LM, model kartından): Pixel 11 Pro TPU 8,3 ms,
MacBook Pro M5 GPU 9,5 ms, iPhone 18 Pro GPU 11,6 ms, Raspberry Pi 5 CPU 161 ms.

## Kaynaklar

- [Hugging Face model kartı](https://huggingface.co/google/embeddinggemma-2)
- [Duyuru](https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/) ve [geliştirici rehberi](https://developers.googleblog.com/embeddinggemma-2-the-developer-guide/)
- [Google AI Edge ve LiteRT](https://developers.googleblog.com/google-ai-edge-with-embeddinggemma-2)
- [İnce ayar rehberi](https://ai.google.dev/gemma/docs/embeddinggemma/fine-tuning-embeddinggemma-with-sentence-transformers) · [Unsloth](https://unsloth.ai/docs/models/embeddinggemma-2)

!!! tip
    Demo uygulamasında bir **EmbeddingGemma** filtresi var: bu sayfadaki her şey orada Türkçe ve İngilizce aranabilir.
