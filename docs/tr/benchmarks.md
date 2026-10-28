# Ölçümler

Konuşmacının dizüstünde ölçüldü: Intel Core Ultra X7 358H, Arc B390 iGPU, Intel NPU, 32 GB RAM, Fedora.
Yalnızca metin modeli, kısa sorgular, tek tek (batch 1). Betikler `bench/` ve `workshop/06_runtimes.py` içinde.

## Sorgu gecikmesi

| Runtime | Yükleme | ms / sorgu | PyTorch'a kosinüs |
|---|---|---|---|
| PyTorch CPU (bf16) | 4,8 sn | 23 | 1,0000 |
| PyTorch XPU (Arc B390) | 2,5 sn | 43 | 1,0000 |
| LiteRT CPU (int4 QAT, 165 MB) | 0,3 sn | 40 | 0,988 |
| LiteRT GPU (Vulkan üzerinden WebGPU) | 0,6 sn | 17 | 0,985 |
| OpenVINO GPU (sabit 256 token) | ilk seferde 13 sn, sonra önbellekten | **6,6** | 1,0000 |
| Tarayıcı WebGPU, q4 (varsayılan) | 175 MB indirme | 160 | 0,98 |
| Tarayıcı WebGPU, fp16 (`?dtype=fp16`) | 543 MB indirme | 31 | 1,0000 |
| Tarayıcı WebGPU, q4f16 (`?dtype=q4f16`) | 157 MB indirme | 29 | 0,91 |
| Tarayıcı WASM, fp16 (WebGPU yoksa) | 543 MB indirme | 116 | 1,0000 |

Tarayıcı satırları: Arc B390 üzerinde Chrome (yazılım yedeği değil, gerçek `xe-3lpg` adaptörü), 10 sıcak sorgunun medyanı,
PyTorch'a kosinüs 8 sorgu üzerinden (`bench/browser_time.mjs`, `bench/browser_vectors.mjs`). q4 varsayılan kalıyor çünkü 175 MB konferans Wi-Fi'ı için makul; hızlı bağlantıda
`?dtype=fp16` 5 kat daha hızlı ve birebir doğru. q4f16 hızlı ama 8 sorgunun 3'ünde ilk sonucu değiştirdi, bu yüzden kullanmıyoruz.

## İndeksleme

| İş | CPU | GPU |
|---|---|---|
| 256 kısa belge (metin modeli, batch 32) | saniyede 61 belge | saniyede 176 belge (XPU) |
| Atölyenin 141 belgesi | 14 sn | |
| 100 fotoğraf (görsel kodlayıcı, görsel başına 280 token) | 257 sn | 16 sn (XPU, batch 1) |

!!! note "XPU ve fotoğraflar"
    torch 2.15 XPU'da int64 tensörlerde `max(dim=...)` elemanların yaklaşık üçte birini atlıyor. Görsel kodlayıcı
    yama ızgarasının genişliğini bununla bulduğu için bazı fotoğraflar `split_with_sizes` hatası veriyordu.
    `TorchEmbedder` XPU'da bu adımı int32 ile yapıyor; 100 fotoğrafın hepsi CPU ile aynı sonucu veriyor (kosinüs en az 0,9995).
    Yeniden üretmek için: `bench/vision_xpu_repro.py`.

## Arama kalitesi

147 belge üzerinde, çoğu diller arası 72 soru. İndeks PyTorch ile kuruldu.

| boyut | recall@1 | recall@3 | MRR | recall@1, LiteRT sorguları |
|---|---|---|---|---|
| 768 | 0,83 | 0,97 | 0,902 | 0,83 |
| 512 | 0,81 | 0,99 | 0,885 | 0,79 |
| 256 | 0,78 | 0,99 | 0,873 | 0,72 |
| 128 | 0,72 | 0,86 | 0,803 | 0,67 |

## Sunucu

| | |
|---|---|
| Konteyner imajı (FastAPI + LiteRT, PyTorch yok) | ~575 MB |
| Soğuk açılış | ~1,1 sn |
| RAM | ~200 MB |
| İstek (sorgu embedding'i + niyet yönlendirme) | CPU'da ~80 ms |

## NPU

- **LiteRT-LM**: `NPU is supported only for Intel OpenVINO on Windows.` `_Intel_PTL.litertlm` dosyası Windows'u hedefliyor.
- **Linux'ta OpenVINO**: model CPU ve GPU'da derleniyor ve PyTorch ile birebir eşleşiyor, ama NPU derleyicisi reddediyor
  (`ZE_RESULT_ERROR_INVALID_ARGUMENT`). Yeniden üretmek için: `bench/openvino_npu.py`.
