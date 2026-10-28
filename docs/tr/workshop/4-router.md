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
    "food": "food, eating, restaurants, street food, breakfast / yemek, kahvaltı, tatlı",
    "devfest": "DevFest conference, tickets, venue, speakers / konferans, bilet, etkinlik",
    ...
}
labels = embedder.embed([classification(d) for d in CATEGORIES.values()])   # bir kez
scores = labels @ embedder.embed([classification(question)])[0]             # her soru için
```

Web uygulaması bunu her cevabın yanında bir **niyet** rozeti göstermek için kullanıyor. MediaPipe'ın Decision Task'ı
aynı fikri Android, iOS ve web için hazır paket olarak sunuyor.

## Dene

- [ ] Bir `sports` kategorisi ekle. Hangi sorular ona kayıyor?
- [ ] Tarifleri sadece Türkçe yaz. İngilizce sorular hâlâ doğru yere gidiyor mu?
