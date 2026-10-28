# 1. Embedding'ler

**Embedding**, bir içeriğin *ne anlama geldiğini* temsil eden sayı listesidir (burada 768 sayı).
Anlamı yakın metinlerin vektörleri benzer yönlere bakar. Bu yüzden *"where can I eat a fish sandwich?"* ile
*"Balık ekmek, Eminönü'nde satılan balık sandviçi"* tek bir ortak kelimeleri olmasa ve farklı dillerde olsalar bile birbirine yakın düşer.

```bash
uv run workshop/00_setup_check.py
uv run workshop/01_hello_embeddings.py
```

## Sadece ihtiyacın olanı yükle

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "google/embeddinggemma-2",
    config_kwargs={"vision_config": None, "audio_config": None},  # sadece metin: 740M yerine 270M
)
```

## Görev önekleri

EmbeddingGemma 2, vektörün ne için kullanılacağını söyleyen kısa öneklerle eğitildi.
Arama **asimetrik**: sorgu ve belge farklı önek alır.

| Kullanım | Sorgu | Belge |
|---|---|---|
| arama | `task: search result \| query: {soru}` | `title: {başlık} \| text: {içerik}` |
| soru cevaplama | `task: question answering \| query: {soru}` | yukarıdakiyle aynı |
| kod arama | `task: code retrieval \| query: {soru}` | `title: {dosya} \| text: {kod}` |
| sınıflandırma, kümeleme, benzerlik | `task: classification \| query: {metin}` (iki tarafta da aynı) | |

sentence-transformers yaygın olanları ismen tanır:

```python
doc_emb = model.encode(documents, prompt_name="Document")       # "title: none | text: "
query_emb = model.encode(queries, prompt_name="SearchQuery")    # "task: search result | query: "
scores = model.similarity(query_emb, doc_emb)                   # kosinüs benzerliği
```

Kendi kodumuzda bu metinleri kendimiz kuruyoruz (`nerede/prompts.py`); böylece gerçek başlıkları kullanabiliyor
ve her runtime'a birebir aynı metni gönderebiliyoruz.

## Dene

- [ ] İki `encode()` çağrısından da `prompt_name=` kısmını sil. Skorlar kötüleşiyor mu?
- [ ] Bildiğin başka bir dilde bir cümle ekle. Doğru belgeyi yine buluyor mu?
- [ ] `"yüz"` kelimesini `"yüz yaşında"` ve `"denizde yüz"` ile karşılaştır. Bağlam hakkında ne söylüyor?
