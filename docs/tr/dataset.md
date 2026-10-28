# Veri seti

Tüm veri `data/` altında JSON Lines biçiminde: her satırda bir kayıt; okuması, karşılaştırması ve genişletmesi kolay.

| Dosya | Kayıt | İçerik |
|---|---|---|
| `istanbul.jsonl` | 101 | yerler, yemekler, ulaşım ve ipuçları (52 Türkçe, 49 İngilizce) |
| `devfest.jsonl` | 16 | DevFest İstanbul 2026 ve GDG İstanbul (8 TR, 8 EN) |
| `embeddinggemma.jsonl` | 24 | model hakkında notlar (12 TR, 12 EN) |
| `images.jsonl` + `images/` | 100 | her yer için bir fotoğraf, yazarı ve lisansıyla |
| `eval_queries.jsonl` | 66 | doğru cevabın kimliğiyle birlikte sorular |

## Bir yer kaydı

```json
{"id": "galata-kulesi", "title": "Galata Kulesi", "district": "Beyoğlu", "category": "view", "lang": "tr",
 "text": "1348'de Cenevizliler tarafından inşa edilen taş kule, Haliç ve tarihi yarımadanın en iyi panoramik manzaralarından birini sunar. Gün batımında seyir terasında sıra oluşabilir.",
 "source": "https://tr.wikipedia.org/wiki/Galata_Kulesi", "wiki_en": "Galata Tower", "wiki_tr": "Galata Kulesi",
 "lat": 41.02555556, "lon": 28.97416667}
```

Her belge bilerek **tek** dilde yazıldı. Türkçe bir soru İngilizce belgeleri, İngilizce bir soru Türkçe belgeleri bulmak
zorunda; çok dilli bir embedding modeli tam olarak bunun için var.

## Nasıl doğrulandı

- **Yerler**: her kayıt doğrulandığı Wikipedia maddesini (`source`) gösteriyor. İlk 51 kayıt İngilizce ve Türkçe Wikipedia'ya
  karşı kontrol edildi ve 13'ü düzeltildi (örneğin Ayasofya 1934'te değil 1935'te müze olarak açıldı; Adalar dört değil
  dokuz adadan oluşuyor). Sonraki 50 kayıt doğrudan Wikipedia'dan yazıldı. Wikipedia'nın kapsamadığı 16 pratik ipucu
  (balık ekmeğin yanında turşu suyu gibi) ikinci kez resmi siteler ve gezi rehberleriyle kontrol edildi: 11'i doğrulandı,
  5'i yeniden yazıldı (örneğin Boğaz vapuru artık "şehri denizden görmenin en ucuz yolu" diye anlatılmıyor). İki turun
  tüm kaynakları `data/drafts/factcheck_report.md` ve `data/drafts/factcheck_round2.md` dosyalarında.
- **DevFest**: yalnızca [devfest.istanbul](https://devfest.istanbul/) ve arşivindeki bilgiler, 2025 tarihi için bir Webrazzi
  haberi. Tarih, mekân ve bilet fiyatları 28 Ekim 2026'da site ve Kommunity ile yeniden kontrol edildi; fiyatlar değişebilir.
- **EmbeddingGemma**: yalnızca model kartları ve Google'ın duyuru yazılarındaki bilgiler.

!!! warning "Alıntılamadan önce bir daha kontrol et"
    Veri bir atölye demosu için hazırlandı. Bir hata görürsen satırı düzelt ve indeksi yeniden kur.

## Fotoğraflar ve lisanslar

`scripts/fetch_images.py` her yerin Wikipedia maddesindeki ana görseli Wikimedia Commons'tan indirir ve yalnızca lisansı
CC0, CC BY, CC BY-SA, Free Art License ya da kamu malı ise tutar. İki logo gerçek fotoğraflarla değiştirildi.
Her fotoğrafın yazarı, lisansı ve kaynak sayfası `data/images.jsonl` ve `data/images/ATTRIBUTION.md` dosyalarında;
uygulama da her fotoğrafın altında bu bilgiyi gösteriyor.

## Kendin ekle

1. `data/istanbul.jsonl` dosyasına (ya da başka bir koleksiyona) benzersiz `id` ile bir satır ekle.
2. İstersen fotoğraf ekle: `data/images/<id>.jpg` dosyasını koy ve `data/images.jsonl` dosyasına bir satır yaz.
3. `uv run workshop/02_build_index.py` çalıştır ve ara.
