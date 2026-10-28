# 7. Fotoğraf arama

EmbeddingGemma 2 **görselleri, sesi ve videoyu metinle aynı 768 boyutlu uzaya** yerleştirir.
Böylece görsel kodlayıcıyla bir kez indekslenen bir fotoğraf, sonradan sadece kelimelerle bulunabilir, hatta
sunucudaki küçük, yalnızca metin bilen LiteRT modeliyle bile.

```bash
# 106 İstanbul fotoğrafı
uv run workshop/03_search.py --photos
# kendi fotoğrafların, hiçbir şey bilgisayarından çıkmaz
uv run workshop/07_photo_search.py ~/Pictures
# sorgu olarak bir fotoğraf
uv run workshop/08_image_search.py data/query_images/yerebatan.jpg
```

## Nasıl çalışıyor

```python
# metin + görsel, 440M
model = SentenceTransformer(
    "google/embeddinggemma-2", config_kwargs={"audio_config": None}
)

# medyaya önek yok
photo_vectors = model.encode([{"image": "data/images/galata-kulesi.jpg"}, ...])
query_vector = model.encode(
    "deniz kenarında taş kule", prompt_name="SearchQuery"
)
model.similarity(query_vector, photo_vectors)
```

İki kural:

1. **Medya görev öneki almaz.** Sadece metin alır.
2. Metnin içinde `<|image|>`, `<|video|>` ve `<|audio|>` medya için yer tutuculardır. Bir belge bu işaretlerden
   *bahsediyorsa* onları etkisizleştir, yoksa işlemci hiç gelmeyecek bir görseli bekler
   (`nerede/prompts.py` bunu senin için yapıyor).

## Fotoğrafla ara { #by-photo }

Sorgu bir fotoğraf da olabilir. Fotoğraf, indeksteki fotoğraflar gibi öneksiz olarak görsel kodlayıcıdan geçer ve
vektörü diğer her şeyle aynı uzaya düşer. Böylece tek bir sorgu vektörü iki şey bulur:

- **benzer fotoğraflar** (görselden görsele): aynı yerin indeksteki fotoğrafı
- **eşleşen yerler** (görselden metne): Türkçe ya da İngilizce yazılmış yer açıklamaları

```bash
uv run workshop/08_image_search.py data/query_images/kunefe.jpg
uv run workshop/08_image_search.py --eval   # modelin hiç görmediği 27 fotoğraf
```

Uygulamada arama çubuğundaki kameraya tıkla, fotoğrafı sayfanın herhangi bir yerine bırak ya da yapıştır (Ctrl+V).
Fotoğraf, sen kaldırana kadar çubukta küçük bir kart olarak durur.

- **Tarayıcı** modu, [canlı demo](../../../demo/) dahil: ilk fotoğraf görsel kodlayıcıyı indirir (WebGPU ile yaklaşık
  109 MB), sonra fotoğraf cihazından hiç çıkmaz.
- **Sunucu** modu: sunucuda PyTorch varsa çalışır, yani kendi bilgisayarında çalıştırdığında. LiteRT konteyneri
  yalnızca metin bilir, bu yüzden orada kamerayı gizler.

### Fotoğraf artı kelimeler

Fotoğrafın yanına kelime yazarsan ikisi tek bir sorguya girer: `normalize(photo + text)`. Kelimeler fotoğrafı
yönlendirir. Önünde vapur olan Galata Kulesi fotoğrafı tek başına Boğaz turunu, `kule` ile Galata Kulesi'ni getirir.
Köprünün önündeki bir bardak çay tek başına çayı, `bridge` ile Boğaziçi Köprüsü'nü getirir. Fotoğrafı ve metni
modele birlikte vermek (`"... <|image|>"`) aşağı yukarı aynı sonucu verdi. İki vektörü toplamak ise daha ucuz:
fotoğraf bir kez gömülür, kelimeler değişince yalnızca metin yeniden gömülür.

Her yerin bir fotoğrafı ve bir metni var, bu yüzden `Index.search_by_photo` ikisine de oy verdirir. Metin puanları
fotoğraf puanlarından yaklaşık 0,08 düşük çıkar. Önce fotoğraf ölçeğine kaydırılır, sonra ikisinin ortalaması alınır:

```python
photo = place_photo_vectors @ q  # görselden görsele
text = place_text_vectors @ q  # görselden metne
score = (photo + text + photo.mean() - text.mean()) / 2
```

`data/query_images/` altındaki sorgu fotoğrafları, indeksteki 27 yerin Wikimedia Commons'taki başka fotoğrafları.
Elle seçildiler ve model bunları hiç görmedi. Doğru yer ilk 1 / ilk 3 içinde:

| boyut | görsel → görsel | görsel → metin | ikisi birden |
|---|---|---|---|
| 768 | 0,63 / 0,78 | 0,48 / 0,70 | **0,74 / 0,85** |
| 512 | 0,59 / 0,74 | 0,52 / 0,67 | **0,74 / 0,85** |
| 256 | 0,56 / 0,78 | 0,41 / 0,63 | **0,67 / 0,81** |
| 128 | 0,56 / 0,74 | 0,37 / 0,56 | **0,63 / 0,85** |

Iskalanlara bakmaya değer. Önünde vapur olan bir Galata Kulesi fotoğrafı Boğaz turu olarak dönüyor, Rumeli Hisarı
karşı kıyıdaki ikizi Anadolu Hisarı ile yer değiştiriyor, Türk kahvesi de çayın yanına düşüyor. 27 fotoğrafta tek bir
fotoğraf sonucu yaklaşık 0,04 oynatır, bu yüzden tabloyu kaba bir yol gösterici olarak oku.

## Fotoğraflar

106 fotoğrafın hepsi Wikimedia Commons'tan ve CC BY, CC BY-SA, Free Art License ya da kamu malı lisanslı.
`scripts/data/fetch_images.py` her yerin Wikipedia maddesindeki ana görseli alır, lisansını kontrol eder ve emeği geçenleri
`data/images/ATTRIBUTION.md` dosyasına yazar. Uygulama her fotoğrafın altında yazarını ve lisansını gösterir.
Sorgu fotoğrafları `scripts/data/fetch_query_images.py` ile geliyor, emeği geçenler `data/query_images/ATTRIBUTION.md` dosyasında.

## Dene

- [ ] Yalnızca **Fotoğraflar** filtresini açık bırakıp `"sokak yemeği"` ara. Hangi yemekler geliyor?
- [ ] Telefonundaki bir fotoğrafla ara: bir sokak, bir yemek, bir vapur. İlk sırada hangi yer geliyor?
- [ ] `08_image_search.py --eval --dim 128` çalıştır ve ıskalananları 768 boyutla karşılaştır.
- [ ] İngilizce bir ifadeyle ara: `"a stone tower by the sea"`.
- [ ] Modaliteleri karıştır: `model.encode({"text": "Bir gün <|image|>", "image": "foto.jpg"})` bir gönderiyi fotoğrafıyla birlikte tek vektöre gömer.
