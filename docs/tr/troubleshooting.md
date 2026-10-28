# Sorun giderme

??? question "`tatlı` ya da `dessert` gibi tek kelimelik aramalar tuhaf sonuçlar veriyor"
    Tek kelime çok az anlam taşıyor, bu yüzden bütün yemek kayıtları neredeyse aynı puanı alıyor (0,70-0,73) ve
    sıralama rastgeleye yakın oluyor. İki şey işe yarar. Soruyu cümle olarak yaz: "sütlü tatlı" ya da "baklava nerede
    yenir", "tatlı"dan çok daha iyi ayrışıyor. Belgelerin de ne olduklarını söylediğinden emin ol: "tatlı" ve "dessert"
    kelimelerini kullanan altı tatlı eklenmeden önce "tatlı" aramasının ilk 5'inde simit ve salep vardı. Şimdi 5'i de tatlı.
    Bir ve iki kelimelik sorgularda hibrit arama artık varsayılan olarak açık (yönlendirici niyeti + anahtar kelime) ve
    tek kelimelik sorgularda precision@5'i 0,68'den 0,86'ya çıkarıyor. Bkz. [Yönlendirici + anahtar kelime](workshop/4-router.md#hybrid).

??? question "`uv run` 5 GB CUDA kütüphanesi indiriyor"
    Linux'ta varsayılan PyTorch CUDA'lı sürüm. Bu proje `cpu` bağımlılık grubuyla CPU sürümünü varsayılan yapıyor.
    `--no-default-groups` verdiysen CUDA sürümünü bilerek alıyorsun. Bkz. [Kurulum](setup.md).

??? question "`ValueError: Found 1 <|image|> tokens in the text but no images were passed`"
    Görsel ya da ses kodlayıcısı yüklüyken bir metinde düz `<|image|>`, `<|video|>` veya `<|audio|>` geçiyor.
    Bunlar medya yer tutucuları. Düz metni gömmeden önce etkisizleştir. `nerede/prompts.py` bunu yapıyor.

??? question "Skorlar iyi görünüyor ama 256 ya da 128 boyutta sıralama kötüleşiyor"
    Matryoshka vektörünü kestikten sonra yeniden normalize et, sorgu ve belgeler için aynı boyutu kullan.

??? question "LiteRT dokümanındaki görev önekleri farklı görünüyor"
    LiteRT-LM sayfası `task: search query | text:` yazıyor, model kartı ise `task: search result | query:` ve
    `title: … | text: …` kullanıyor. Bu atölye her runtime'da model kartının biçimini kullanıyor ve değerlendirme bunun
    LiteRT ile de çalıştığını gösteriyor.

??? question "OpenVINO: `Path '…onnx_data' … is outside the base directory`"
    OpenVINO, Hugging Face önbelleğinin kullandığı sembolik bağlantılı ONNX harici verisini kabul etmiyor.
    `hf download … --local-dir` ile indir ya da `OpenVINOEmbedder` gibi doğrudan PyTorch'tan dönüştür.

??? question "OpenVINO, onnx-community ONNX dosyasıyla yanlış vektör veriyor"
    Konuşmacının dizüstünde `model_fp16.onnx` dosyasını doğrudan OpenVINO'da okumak PyTorch'tan uzak vektörler verdi (kosinüs 0,6-0,8),
    onnxruntime ise doğru sonuç verdi. PyTorch'tan dönüştürmek birebir doğru sonuç veriyor, `OpenVINOEmbedder` da bunu yapıyor.

??? question "XPU'da fotoğraf indekslerken `split_with_sizes` hatası"
    torch 2.15 XPU, int64 tensörlerde `max(dim=...)` için yanlış değer döndürüyor ve bu, bazı fotoğraflarda görsel
    havuzlamayı bozuyor. `nerede.embedders.TorchEmbedder` XPU'da bunu düzeltiyor. sentence-transformers'ı doğrudan kullanıyorsan
    fotoğrafları CPU'da işle ya da `nerede/embedders.py` içindeki `_fix_xpu_vision_pooling` fonksiyonunu kopyala.

??? question "Rootless podman ile `curl localhost:8080` bağlantıyı kesiyor"
    `localhost` IPv6 `::1` adresine çözülebiliyor ve rootless podman bunu yönlendirmiyor. `127.0.0.1` kullan.

??? question "Tarayıcı modu yavaş ya da açılmıyor"
    WebGPU ile ilk çalıştırma yaklaşık 175 MB indiriyor. WebGPU yoksa (`chrome://gpu` ile kontrol et) sayfa fp16 modelle
    WASM kullanır, yaklaşık 543 MB, çünkü q4 ve q8 dosyaları WASM tarafında olmayan `GatherBlockQuantized` işlemini kullanıyor
    (`Could not find an implementation for GatherBlockQuantized`). WebGPU'da her batch'i yaklaşık 2.700 token'ın altında tut.

??? question "LiteRT çok fazla log basıyor"
    `LiteRTEmbedder` log seviyesini ERROR yapıyor. Kendi kodunda motoru oluşturmadan önce
    `litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)` çağır.
