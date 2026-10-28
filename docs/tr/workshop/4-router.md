# 4. Sıfır-örnek yönlendirici

Eğitim verisi olmadan sınıflandırma: her kategoriyi bir cümleyle tarif et, tarifleri bir kez göm ve her soruyu
en yakın kategoriye ata.

```bash
uv run workshop/05_router.py
```

```text
   nightlife  0.866  akşam rakı içmek için güzel bir yer
   transport  0.784  how do I pay for the metro?
      museum  0.847  çocuklarla gidilecek müze
     devfest  0.868  DevFest bileti ne kadar?
          ai  0.807  how many dimensions does the embedding have
```

Sınıflandırma **simetrik** bir görev, bu yüzden iki tarafa da aynı önek konur:

```python
CATEGORIES = {
    "food": "food, restaurants, street food / yemek, kahvaltı, tatlı",
    "devfest": "DevFest conference, tickets, venue / konferans, bilet",
    ...
}
# bir kez
labels = embedder.embed([classification(d) for d in CATEGORIES.values()])
# her soru için
scores = labels @ embedder.embed([classification(question)])[0]
```

Web uygulaması bunu her cevabın yanında bir **niyet** rozeti göstermek için kullanıyor. MediaPipe'ın Decision Task'ı
aynı fikri Android, iOS ve web için hazır paket olarak sunuyor.

## Yönlendirici + anahtar kelime = hibrit arama { #hybrid }

"tatlı" ya da "müze" gibi tek kelimelik bir sorgu çok az anlam taşıyor: bütün yemek kayıtları neredeyse aynı puanı
alıyor ve simit baklavayı geçebiliyor. Burada yönlendirici yardımcı oluyor. **Bir ya da iki kelimelik** sorgularda
`Index.search` kosinüs puanının üstüne iki küçük katkı ekliyor:

- **niyet**: yönlendiricinin seçtiği kategorideki kayıtlara +0,05, ama yalnızca emin olduğunda (puan 0,79 ya da üstü).
- **anahtar kelime**: başlık ve metin üzerinde BM25'ten en çok +0,03. Türkçeye uygun: "tatli", "tatlı" ve "tatlısı"nı bulur.

```python
# hibrit
hits = index.search(vector, k=5, text=q, intent=router.route(q))
# sadece vektör
hits = index.search(vector, k=5)
```

Daha uzun sorgular düz vektör puanıyla kalıyor, bu yüzden 72 cümlelik sorunun sonucu hiç değişmiyor. 3. adım tek
kelimelik durumu `data/eval_short.jsonl` ile ölçüyor (24 sorgu, ilk 5 sonucun kaçı doğru):

| | vektör | hibrit |
|---|---|---|
| LiteRT sorguları, 768 boyut | 0,68 | **0,86** |
| LiteRT sorguları, 256 boyut | 0,64 | **0,83** |

Sunucu da Tarayıcı modu da bunu kullanıyor. Karşılaştırmak için sayfa adresine `?search=vector` (API'ye `mode=vector`) ekle.
Katkıyı her sorguya uygulamak cümlelik sorularda recall@1'i düşürdü, yönlendirici de bazı tek kelimelerden emin değil
("cami" 0,77 ile `ai`'a gidiyor). İki sınırın nedeni bu.

## Dene

- [ ] Bir `sports` kategorisi ekle. Hangi sorular ona kayıyor?
- [ ] Tarifleri sadece Türkçe yaz. İngilizce sorular hâlâ doğru yere gidiyor mu?
- [ ] `nerede/index.py` içindeki `INTENT_BOOST` ya da `KEYWORD_BOOST` değerini değiştir ve 3. adımı yeniden çalıştır. Nerede zarar vermeye başlıyor?
