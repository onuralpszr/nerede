# Colab defteri

Atölyenin tamamı iki defterde, her dil için bir tane. **Ücretsiz** Colab sürümünde çalışırlar.

| Defter | Aç |
|---|---|
| Türkçe | [![Colab'da aç](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/onuralpszr/nerede/blob/main/notebooks/nerede_tr.ipynb) |
| English | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/onuralpszr/nerede/blob/main/notebooks/nerede_en.ipynb) |

## Defter neler yapıyor

1. **Kurulum**: depoyu klonlar; `sentence-transformers`, `litert-lm-api` ve uygulamayı kurar (Colab'da PyTorch zaten var).
2. **Merhaba embedding**: görev önekleri ve Türkçe ↔ İngilizce benzerlik.
3. **İndeksi kur**: yerler, DevFest bilgileri, EmbeddingGemma notları ve fotoğraflar.
4. **Arama**: metin arama ve metinden fotoğrafa arama, görsellerle birlikte.
5. **Ölçüm**: 768, 512, 256 ve 128 boyutta isabet.
6. **Yönlendirici**: sıfır-örnekle niyet sınıflandırma.
7. **LiteRT**: aynı sorgular 165 MB'lık cihaz modeliyle, PyTorch ile karşılaştırmalı.
8. **Web uygulaması**: FastAPI sunucusunu Colab içinde başlatır ve arayüzün bağlantısını yazar.

## Ücretsiz sürüm için ipuçları

- **Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU** fotoğraf indekslemeyi hızlandırır. GPU yoksa defter CPU'ya geçer.
- Colab bağlantıyı koparırsa **Çalışma zamanı → Tümünü çalıştır** de. Modeller oturum boyunca önbellekte kalır.
- Web uygulaması bağlantısı yalnızca defter çalışırken açılır.

## Kendi bilgisayarında

Defterler Jupyter'da ya da VS Code'da da çalışır:

```bash
uv run --with jupyterlab jupyter lab notebooks/
```
