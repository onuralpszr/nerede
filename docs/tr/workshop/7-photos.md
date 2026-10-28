# 7. Fotoğraf arama

EmbeddingGemma 2 **görselleri, sesi ve videoyu metinle aynı 768 boyutlu uzaya** yerleştirir.
Böylece görsel kodlayıcıyla bir kez indekslenen bir fotoğraf, sonradan sadece kelimelerle bulunabilir; hatta
sunucudaki küçük, yalnızca metin bilen LiteRT modeliyle bile.

```bash
uv run workshop/03_search.py --photos          # 106 İstanbul fotoğrafı
uv run workshop/07_photo_search.py ~/Pictures  # kendi fotoğrafların, hiçbir şey bilgisayarından çıkmaz
```

## Nasıl çalışıyor

```python
model = SentenceTransformer("google/embeddinggemma-2", config_kwargs={"audio_config": None})  # metin + görsel, 440M

photo_vectors = model.encode([{"image": "data/images/galata-kulesi.jpg"}, ...])   # medyaya önek yok
query_vector = model.encode("deniz kenarında taş kule", prompt_name="SearchQuery")
model.similarity(query_vector, photo_vectors)
```

İki kural:

1. **Medya görev öneki almaz.** Sadece metin alır.
2. Metnin içinde `<|image|>`, `<|video|>` ve `<|audio|>` medya için yer tutuculardır. Bir belge bu işaretlerden
   *bahsediyorsa* onları etkisizleştir; yoksa işlemci hiç gelmeyecek bir görseli bekler
   (`nerede/prompts.py` bunu senin için yapıyor).

## Fotoğraflar

106 fotoğrafın hepsi Wikimedia Commons'tan; CC BY, CC BY-SA, Free Art License ya da kamu malı lisanslı.
`scripts/fetch_images.py` her yerin Wikipedia maddesindeki ana görseli alır, lisansını kontrol eder ve emeği geçenleri
`data/images/ATTRIBUTION.md` dosyasına yazar. Uygulama her fotoğrafın altında yazarını ve lisansını gösterir.

## Dene

- [ ] Yalnızca **Fotoğraflar** filtresini açık bırakıp `"sokak yemeği"` ara. Hangi yemekler geliyor?
- [ ] İngilizce bir ifadeyle ara: `"a stone tower by the sea"`.
- [ ] Modaliteleri karıştır: `model.encode({"text": "Bir gün <|image|>", "image": "foto.jpg"})` bir gönderiyi fotoğrafıyla birlikte tek vektöre gömer.
