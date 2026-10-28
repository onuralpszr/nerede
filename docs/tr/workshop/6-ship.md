# 6. Yayına al

## Uygulamayı çalıştır

```bash
NEREDE_BACKEND=litert uv run uvicorn app.main:app --reload
```

<http://127.0.0.1:8000> adresini aç. Sayfanın iki modu var:

- **Sunucu**: tarayıcı `/api/search` ve `/api/photos` uçlarını çağırır, sorguyu sunucuda LiteRT gömer.
- **Tarayıcı**: sayfa modeli indirir (sonra önbellekten gelir) ve `index.json` üzerinde yerel olarak arar.
  Soru cihazdan hiç çıkmaz. WebGPU varsa 4 bitlik modeli (~175 MB) kullanır. WebGPU yoksa fp16 ile WASM'a (~543 MB) geçer,
  çünkü 4 ve 8 bitlik dosyalar WASM tarafında olmayan bir çekirdeğe ihtiyaç duyuyor. Bu yolu denemek için adrese
  `?device=wasm` ekle.

| Uç | Örnek |
|---|---|
| `GET /api/search` | `/api/search?q=balık ekmek&collection=places&dim=256&k=6` |
| `GET /api/photos` | `/api/photos?q=kubbeli cami&k=12` |
| `GET /api/health` | backend, koleksiyon boyutları, fotoğraf sayısı |

Bağlantılar paylaşılabilir: `/?q=DevFest ne zaman&tab=devfest`.

## Konteyner kur

```bash
docker build -t nerede .        # ya da: podman build -t nerede .
docker run -p 8080:8080 nerede  # http://127.0.0.1:8080
```

İmajda FastAPI, LiteRT ve 165 MB'lık model var ama PyTorch yok.
Yaklaşık 575 MB, yaklaşık bir saniyede açılıyor ve 200 MB civarı RAM kullanıyor.

## Ücretsiz yayınla

=== "GitHub Pages (statik)"

    API yoksa sayfa tarayıcı moduna geçer; yani demo düz dosyalardan oluşabilir:

    ```bash
    uv run scripts/build_docs.py --with-demo
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

    Ayrı bir oturumda gelecek (ücretsiz kota bir demo için yeterli olsa da faturalandırma hesabı istiyor).
