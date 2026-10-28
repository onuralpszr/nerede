# 3. Tahmin etme, ölç

"Güzel görünüyor" bir metrik değil. `data/eval_queries.jsonl` içinde 72 soru var, her birinin yanında ilk sırada
gelmesi gereken belgenin kimliği yazıyor. Çoğu **diller arası**: İngilizce belge için Türkçe soru ya da tersi.

```bash
uv run workshop/04_matryoshka_eval.py
# torch indeksi, LiteRT sorguları
uv run workshop/04_matryoshka_eval.py --query-backend litert
```

```text
index: torch:cpu   queries: torch:cpu   n=72

  dim  recall@1  recall@3    MRR  bytes/vec   1M docs
  768      0.83      0.97  0.902       3072    2.86GB
  512      0.81      0.99  0.885       2048    1.91GB
  256      0.78      0.97  0.872       1024    0.95GB
  128      0.72      0.86  0.803        512    0.48GB
```

- **recall@1**: doğru cevap ne sıklıkla birinci. **recall@3**: ilk üçte.
- **MRR**: ortalama karşılıklı sıra; 1,0 her zaman birinci, 0,5 genelde ikinci demek.

## Matryoshka: daha küçük vektör, neredeyse aynı cevaplar

EmbeddingGemma 2, bir vektörün **ilk** 512, 256 ya da 128 sayısı tek başına iyi bir embedding olacak şekilde eğitildi.
Baştan kes, sonra yeniden normalize et:

```python
def truncate(v, dim):
    v = v[..., :dim]
    # bunu atlamak sıralamayı sessizce bozar
    return v / np.linalg.norm(v, axis=-1, keepdims=True)
```

Sorgu ve belgeler **aynı** boyutta olmalı. 256 boyutta depolamanın üçte biriyle recall@3'ü %98'de tutuyoruz.
128 boyut altı kat tasarruf sağlıyor ama düşüş görünür durumda. Bu yüzden kendi verinde ölçmelisin.

## Kaçanları oku

Betik 768 boyutta yanlış bildiği her soruyu yazdırır. En ilginç kısım bunlar:

```text
miss at 768d: "Mimar Sinan'ın en ünlü camisi" -> semsi-pasa (expected suleymaniye)
miss at 768d: 'when is the conference this year' -> devfest-2025-stats (expected devfest-ne-zaman)
```

Şemsi Paşa da bir Sinan camisi; iki belge de bir yıldan söz ederken "bu yıl"ı eşleştirmek zor.
Çoğu zaman çözüm modelde değil veride: daha net yazılmış bir belge.

## Tek kelimelik sorgular

Betik ikinci bir testle bitiyor: "tatlı", "müze" ya da "tickets" gibi 24 tek kelimelik sorgu ve her biri için doğru
sayılan kayıtlar. İlk 5 sonucun kaçının doğru olduğunu hem düz vektör aramasıyla hem de [4. adımdaki](4-router.md#hybrid)
hibrit katkılarla gösteriyor:

```text
one-word queries, precision@5, n=24
  dim  vector  hybrid
  768    0.68    0.83
  256    0.69    0.80
```

## Dene

- [ ] `data/eval_queries.jsonl` dosyasına kendi beş sorunu yaz. Hangileri tutmuyor?
- [ ] Bir belgeyi düzelt ki kaçan bir soru isabete dönsün. Yeniden kur ve çalıştır.
