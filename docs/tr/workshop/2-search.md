# 2. İndeks ve arama

Her belgeyi **bir kez** göm, vektörleri sakla, sorgu anında sadece soruyu göm.
Anlamsal arama indeksi bundan ibaret.

```bash
uv run workshop/02_build_index.py --no-images     # 147 belge, dizüstü CPU'da ~15 sn
uv run workshop/03_search.py                       # Türkçe ya da İngilizce sor
uv run workshop/03_search.py --collection devfest devfest2025
uv run workshop/03_search.py --photos              # metinden fotoğrafa (fotoğraf indeksi gerekir)
```

!!! info "Fotoğraflar daha uzun sürer"
    `--no-images` olmadan 2. adım görsel kodlayıcıyı da yükler ve 106 fotoğrafı gömer. Bu dizüstü CPU'da yaklaşık
    4 dakika, GPU'da bir dakikanın altında sürer. Depoda fotoğraflı hazır bir indeks zaten var; bu adımı atlasan da
    fotoğraf aramayı kullanabilirsin.

## İndeks sadece numpy

```python
texts = [document(d["text"], title=d["title"]) for d in docs]
vectors = embedder.embed(texts)                    # (147, 768), birim uzunlukta

q = embedder.embed([query("balık ekmek nerede yenir")])[0]
scores = vectors @ q                               # her şey normalize olduğu için kosinüs benzerliği
best = scores.argsort()[::-1][:5]
```

`nerede/index.py` bunun üstüne üç şey ekliyor: koleksiyon filtresi, fotoğraf vektörleri ve Matryoshka kesmesi.
On binlerce belge için bu yeterince hızlı. Milyonlarca vektör, kalıcılık ya da zengin filtreleme gerektiğinde
Qdrant, sqlite-vec veya pgvector kullan.

## Başlıklar önemli

Belgeler `title: none | text: ...` yerine `title: Balık ekmek | text: ...` olarak gömülüyor.
Model kartı başlık varsa kullanılmasını öneriyor; kısa belgelerde çok fark yaratıyor.

## Dene

- [ ] `"yağmurlu gün"` aramasını önce `--collection places`, sonra `all` ile yap.
- [ ] Aynı soruyu Türkçe ve İngilizce sor. İlk sonuç aynı mı?
- [ ] En sevdiğin yeri `data/istanbul.jsonl` dosyasına ekle, indeksi yeniden kur ve bul.
