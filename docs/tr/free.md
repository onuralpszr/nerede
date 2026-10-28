# Ücretsiz seçenekler

Bu atölyenin her parçası **hiç ödeme yapmadan ve kredi kartı olmadan** çalışır. Durumuna uyanı seç.

| Elinde olan | Kullan | Maliyet | Ne çalışır |
|---|---|---|---|
| Herhangi bir dizüstü (GPU'suz bile) | yerel, CPU PyTorch | ücretsiz | her şey |
| Sadece tarayıcı | [Google Colab](colab.md) ücretsiz sürüm | ücretsiz | her şey, web uygulaması dahil (Colab bağlantısıyla) |
| Kaggle hesabı | Kaggle Notebooks | ücretsiz | defterdeki her şey |
| Telefon ya da tablet | yayındaki [tarayıcı demosu](#demo) | ücretsiz | tarayıcıda arama |
| Paylaşmak istediğin bir şey | GitHub Pages ya da Hugging Face Space | ücretsiz | herkese açık demo |

## Yerel CPU yeterli

Metin modeli 270M parametreli. Dizüstü işlemcide bir sorguyu 20-40 ms'de gömer, tüm veri setini saniyeler içinde
indeksler. Fotoğraflar (görsel kodlayıcı, 440M) bir kereliğine yaklaşık dört dakika sürer; istersen hazır indeksi kullanabilirsin.
Yaklaşık 3 GB disk ve 4 GB boş RAM yeter.

## Google Colab (ücretsiz)

Defteri [Colab sayfasından](colab.md) aç. Ücretsiz sürüm bir CPU ortamı ya da T4 GPU verir, fazlasıyla yeterli.
Defter her şeyi kurar, indeksi oluşturur, tüm adımları çalıştırır ve sonunda web uygulamasını Colab içinde
başlatıp yeni sekmede açabileceğin bir bağlantı verir.

!!! tip
    Fotoğrafları daha hızlı indekslemek için **Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU** seç. Gerisi CPU'da da hızlı.

## Kaggle Notebooks (ücretsiz)

Kaggle telefon doğrulamasından sonra haftada yaklaşık 30 saat GPU verir. `notebooks/nerede_tr.ipynb` dosyasını yükle,
ayarlardan **Internet**'i aç ve tüm hücreleri çalıştır. Yalnızca Colab'a özel olan web uygulaması hücresi kendiliğinden atlanır.

## Demoyu ücretsiz yayınla { #demo }

Web uygulamasının **yalnızca tarayıcı modu** var: API'ye ulaşamazsa modeli tarayıcıya indirir ve `index.json`
üzerinde yerel olarak arar. Yani tüm demo sadece statik dosyalardan ibaret:

```bash
uv run scripts/build_docs.py --with-demo      # site/ = dokümanlar (EN + TR) + demo/
```

`site/` klasörünü **GitHub Pages**'te yayınla (`.github/workflows/docs.yml` her push'ta bunu yapar),
demo [onuralpszr.github.io/nerede/demo](https://onuralpszr.github.io/nerede/demo/) adresinde yayında olur. Sunucu yok, fatura yok.

## Hugging Face Spaces (ücretsiz CPU)

Sunucu sürümü (LiteRT API + arayüz) için ücretsiz CPU donanımında bir **Docker** Space oluştur, bu depoyu gönder
ve Space README'sinin başındaki ayarlara şunu ekle:

```yaml
sdk: docker
app_port: 8080
```

İmaj yaklaşık 575 MB, yaklaşık bir saniyede açılıyor ve 200 MB civarı RAM kullanıyor; ücretsiz sürümün rahatça içinde.

!!! note "Cloud Run"
    Google Cloud Run'ın da ücretsiz kotası var ama faturalandırma hesabı istiyor. Onu ayrıca ele alacağız.
