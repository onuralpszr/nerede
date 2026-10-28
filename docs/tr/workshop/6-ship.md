# 6. Yayına al

## Uygulamayı çalıştır

```bash
NEREDE_BACKEND=litert uv run uvicorn app.main:app --reload
```

Windows'ta `NEREDE_BACKEND` değişkenini [Kurulum](../setup.md#windows) sayfasındaki gibi ayarla.

<http://127.0.0.1:8000> adresini aç. Sayfanın iki modu var:

- **Sunucu**: tarayıcı `/api/search` ve `/api/photos` uçlarını çağırır, sorguyu sunucuda LiteRT gömer.
- **Tarayıcı**: sayfa modeli indirir (sonra önbellekten gelir) ve `index.json` üzerinde yerel olarak arar.
  Soru cihazdan hiç çıkmaz. WebGPU varsa 4 bitlik modeli (~175 MB) kullanır. WebGPU yoksa fp16 ile WASM'a (~543 MB) geçer,
  çünkü 4 ve 8 bitlik dosyalar WASM tarafında olmayan bir çekirdeğe ihtiyaç duyuyor. Bu yolu denemek için adrese
  `?device=wasm` ekle.

| Uç | Örnek |
|---|---|
| `GET /api/search` | `/api/search?q=balık ekmek&collection=places&dim=256&k=6`, birden çok koleksiyon için `collection`'ı tekrarla |
| `GET /api/photos` | `/api/photos?q=kubbeli cami&k=12` |
| `POST /api/search/image` | fotoğrafı gövde olarak gönder: `curl --data-binary @foto.jpg -H 'Content-Type: image/jpeg' …/api/search/image?q=kule`, `q` isteğe bağlı, sunucuda PyTorch gerekir |
| `GET /api/health` | backend, koleksiyon boyutları, fotoğraf sayısı |

Filtre düğmeleri birleştirilebilir: **Hepsi** her şeyi açar, diğer düğmeler o koleksiyonu dahil eder ya da çıkarır,
**Fotoğraflar** da eşleşen fotoğrafları bir şerit olarak ekler. Bağlantılar paylaşılabilir: `/?q=kaç kişi geldi&only=devfest,devfest2025`.

## Konteyner kur

```bash
docker build -t nerede .        # ya da: podman build -t nerede .
docker run -p 8080:8080 nerede  # http://127.0.0.1:8080
```

İmajda FastAPI, LiteRT ve 165 MB'lık model var ama PyTorch yok.
Yaklaşık 575 MB, yaklaşık bir saniyede açılıyor ve 200 MB civarı RAM kullanıyor.

## Ücretsiz yayınla

=== "GitHub Pages (statik)"

    API yoksa sayfa tarayıcı moduna geçer, yani demo düz dosyalardan oluşabilir:

    ```bash
    uv run --group docs scripts/docs/build_docs.py --with-demo
    ```

    `site/` klasöründe bu doküman (İngilizce ve Türkçe) ve `demo/` altında demo olur.
    `.github/workflows/docs.yml` bunu `main`'e her push'ta yayınlar.

=== "Hugging Face Spaces (sunucu)"

    Bir **Docker** Space oluştur (ücretsiz CPU), bu depoyu gönder ve Space README'sine şunu ekle:

    ```yaml
    sdk: docker
    app_port: 8080
    ```

=== "Cloud Run"

    [![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run/?git_repo=https://github.com/onuralpszr/nerede.git&revision=main)

    Düğme Cloud Shell'i açar, `Dockerfile`'ı derler ve yayına alır. `app.json` 1 GiB bellek ve en fazla 2 örnek
    ister, böylece unutulan bir demo ucuz kalır. Cloud Run faturalandırma hesabı ister, ücretsiz kotası küçük bir
    demoyu karşılar. Konteyner LiteRT'li olduğu için metinle arar ve fotoğraf kamerasını gizler.
