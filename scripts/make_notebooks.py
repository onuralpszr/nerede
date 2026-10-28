"""Write notebooks/nerede_en.ipynb and notebooks/nerede_tr.ipynb from one list of cells.

The code is identical in both; only the text differs. Run after editing this file:

    uv run scripts/make_notebooks.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/onuralpszr/nerede"

SETUP = f'''import os, sys
IN_COLAB = "google.colab" in sys.modules
IN_KAGGLE = "KAGGLE_KERNEL_RUN_TYPE" in os.environ
REPO = "{REPO}"

if IN_COLAB or IN_KAGGLE:
    if not os.path.exists("nerede"):
        !git clone -q --depth 1 {{REPO}} nerede
    %cd nerede
    !pip install -q "sentence-transformers[image]>=6.1" "transformers>=5.18" litert-lm-api fastapi uvicorn
    !pip install -q -e . --no-deps
elif os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")  # running locally from notebooks/

import torch
from nerede.embedders import pick_torch_device
print("torch", torch.__version__, "| device:", pick_torch_device())'''

HELLO = '''from sentence_transformers import SentenceTransformer

model = SentenceTransformer("google/embeddinggemma-2", device=pick_torch_device(),
                            config_kwargs={"vision_config": None, "audio_config": None})  # text only: 270M

documents = [
    "Kız Kulesi, Üsküdar açıklarında küçük bir adacık üzerinde yer alan tarihi bir kuledir.",
    "The Grand Bazaar is one of the largest and oldest covered markets in the world.",
    "Balık ekmek, Eminönü'nde teknelerden satılan ızgara balık sandviçidir.",
]
queries = ["a tower on a tiny island", "where can I eat a fish sandwich?", "eski kapalı çarşı"]

doc_emb = model.encode(documents, prompt_name="Document")
query_emb = model.encode(queries, prompt_name="SearchQuery")
print(model.similarity(query_emb, doc_emb))'''

BUILD = '''import time
from nerede import Index, load_corpus, load_images
from nerede.embedders import TorchEmbedder

docs = load_corpus()
prebuilt = Index.load()                      # shipped with the repo, includes the photo vectors
BUILD_PHOTOS = torch.cuda.is_available()     # ~1 min on a T4, ~4 min on a laptop CPU

embedder = TorchEmbedder(modalities=("text", "image") if BUILD_PHOTOS else ("text",))
start = time.perf_counter()
index = Index.build(embedder, docs)
print(f"{len(docs)} documents in {time.perf_counter() - start:.1f}s on {embedder.name}")

if BUILD_PHOTOS:
    start = time.perf_counter()
    index.add_images(embedder, load_images())
    print(f"{len(index.images)} photos in {time.perf_counter() - start:.1f}s")
else:
    index.images, index.image_vectors = prebuilt.images, prebuilt.image_vectors
    print(f"{len(index.images)} photo vectors taken from the prebuilt index")

if IN_COLAB or IN_KAGGLE:
    index.save()                             # the web app at the end serves this index
    index.export_web("app/static/index.json")'''

SEARCH = '''import base64, html
from IPython.display import HTML, display
from nerede import query
from nerede.index import DATA

photo_of = {img["id"]: img for img in index.images}

def thumb(img, width=160):
    data = base64.b64encode((DATA / "images" / img["file"]).read_bytes()).decode()
    return f'<img src="data:image/jpeg;base64,{data}" width="{width}" title="{html.escape(img["author"] + " · " + img["license"])}">'

def search(text, k=4, collection="all", dim=768):
    q = embedder.embed([query(text)])[0]
    rows = []
    for score, d in index.search(q, k=k, dim=dim, collection=collection):
        pic = thumb(photo_of[d["id"]], 120) if d["id"] in photo_of else ""
        rows.append(f"<tr><td>{pic}</td><td><b>{html.escape(d['title'])}</b> <small>{d['lang'].upper()} · {d['collection']}</small>"
                    f"<br>{html.escape(d['text'])}</td><td>{score:.3f}</td></tr>")
    display(HTML(f"<p><b>{html.escape(text)}</b></p><table>{''.join(rows)}</table>"))

def search_photos(text, k=6):
    q = embedder.embed([query(text)])[0]
    cells = [f"<figure style='display:inline-block;margin:4px'>{thumb(img)}<figcaption>{html.escape(img['title'])} {s:.3f}</figcaption></figure>"
             for s, img in index.search_images(q, k=k)]
    display(HTML(f"<p><b>{html.escape(text)}</b></p>" + "".join(cells)))

search("nerede balık ekmek yenir?")
search("how do I get to the DevFest venue?", collection="devfest")
search("model kaç dil biliyor?", collection="gemma")
search_photos("domes and minarets")'''

EVAL = '''import json
import numpy as np
from nerede.index import ROOT, truncate

evals = [json.loads(l) for l in (ROOT / "data/eval_queries.jsonl").read_text().splitlines() if l]
Q = embedder.embed([query(e["query"]) for e in evals])
ids = [d["id"] for d in index.docs]
gold = np.array([ids.index(e["gold"]) for e in evals])

print(f"{'dim':>5} {'recall@1':>9} {'recall@3':>9} {'MRR':>6}")
for dim in (768, 512, 256, 128):
    scores = truncate(Q, dim) @ truncate(index.vectors, dim).T
    rank = (scores > scores[np.arange(len(gold)), gold][:, None]).sum(1)
    print(f"{dim:>5} {np.mean(rank < 1):>9.2f} {np.mean(rank < 3):>9.2f} {np.mean(1 / (rank + 1)):>6.3f}")'''

ROUTER = '''from nerede.router import Router

router = Router(embedder)
for text in ["akşam rakı içmek için güzel bir yer", "how do I pay for the metro?",
             "DevFest bileti ne kadar?", "how many dimensions does the embedding have"]:
    label, score = router.route(text)
    print(f"{label:>10}  {score:.3f}  {text}")'''

LITERT = '''import time
from nerede.embedders import LiteRTEmbedder

lite = LiteRTEmbedder()                      # 165 MB int4 file, no torch involved
texts = [query(t) for t in ["balık ekmek", "Bizans mozaikleri", "train under the Bosphorus", "DevFest bileti"]]
start = time.perf_counter()
lv = lite.embed(texts)
print(f"LiteRT: {(time.perf_counter() - start) / len(texts) * 1000:.0f} ms per query")
print("cosine vs PyTorch:", np.round((lv * embedder.embed(texts)).sum(1), 4))

q = lite.embed([query("where can I eat a fish sandwich?")])[0]   # LiteRT query, PyTorch-built index
print([d["title"] for _, d in index.search(q, k=3)])'''

APP = '''import subprocess, time, urllib.request

if IN_COLAB:
    env = {**os.environ, "NEREDE_BACKEND": "litert"}
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"], env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/health"); break
        except Exception:
            time.sleep(1)
    from google.colab.output import eval_js
    print("Open the app:", eval_js("google.colab.kernel.proxyPort(8000)"))
else:
    print("Locally, run:  NEREDE_BACKEND=litert uv run uvicorn app.main:app")'''

TEXT = {
    "en": {
        "title": """# Nerede? EmbeddingGemma 2 workshop

**Workshop proposal for GDG DevFest İstanbul 2026.** Build a Turkish-English semantic search over Istanbul places (with photos), DevFest İstanbul 2026 facts and notes about EmbeddingGemma 2 itself, then run the same index with PyTorch, LiteRT and a web app.

Runs on the free Colab tier. For faster photo indexing choose **Runtime → Change runtime type → T4 GPU** (optional).""",
        "setup": "## 0. Setup\nClones the repository on Colab or Kaggle and installs the few extra packages. Locally it just checks your environment.",
        "hello": "## 1. Hello embeddings\nQueries and documents get different **task prompts**. Notice that English questions find Turkish sentences and the other way round.",
        "build": "## 2. Build the index\n147 documents in three collections, plus 106 Wikimedia Commons photos. Photos are embedded only on a GPU; otherwise their vectors come from the prebuilt index in the repo.",
        "search": "## 3. Search\nText search over all collections, and text → photo search. Hover a photo for its author and license.",
        "eval": "## 4. Measure\n66 labelled questions, most of them cross-lingual. Matryoshka lets us keep only the first 512, 256 or 128 numbers of each vector. How much do we lose?",
        "router": "## 5. Zero-shot router\nClassify questions without any training data, using the symmetric `task: classification` prompt.",
        "litert": "## 6. LiteRT\nThe same model as a 165 MB int4 file. Its vectors are close enough to PyTorch's that it can query the PyTorch-built index.",
        "app": "## 7. The web app\nOn Colab this starts the FastAPI app (LiteRT backend) and prints a link. Try the **Browser** mode too: it runs the model inside your browser.",
        "end": "## Next\n- Docs (English and Turkish): see `docs/` or the published site.\n- Host the demo for free: `uv run --group docs scripts/build_docs.py --with-demo` and publish `site/` on GitHub Pages.\n- Add your own places to `data/istanbul.jsonl` and run the notebook again.",
    },
    "tr": {
        "title": """# Nerede? EmbeddingGemma 2 atölyesi

**GDG DevFest İstanbul 2026 atölye önerisi.** İstanbul'daki yerler (fotoğraflarıyla), DevFest İstanbul 2026 bilgileri ve EmbeddingGemma 2 hakkındaki notlar üzerinde Türkçe-İngilizce anlamsal arama kur; sonra aynı indeksi PyTorch, LiteRT ve bir web uygulamasıyla çalıştır.

Ücretsiz Colab sürümünde çalışır. Fotoğrafları daha hızlı indekslemek için **Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU** seçebilirsin (isteğe bağlı).""",
        "setup": "## 0. Kurulum\nColab ya da Kaggle'da depoyu klonlar ve birkaç ek paketi kurar. Kendi bilgisayarında sadece ortamı kontrol eder.",
        "hello": "## 1. Merhaba embedding\nSorgular ve belgeler farklı **görev önekleri** alır. İngilizce soruların Türkçe cümleleri bulduğuna, tersinin de çalıştığına dikkat et.",
        "build": "## 2. İndeksi kur\nÜç koleksiyonda 147 belge ve Wikimedia Commons'tan 106 fotoğraf. Fotoğraflar yalnızca GPU varsa gömülür; yoksa vektörleri depodaki hazır indeksten gelir.",
        "search": "## 3. Arama\nTüm koleksiyonlarda metin arama ve metinden fotoğrafa arama. Yazarını ve lisansını görmek için fareyi fotoğrafın üzerine getir.",
        "eval": "## 4. Ölçüm\nÇoğu diller arası 72 etiketli soru. Matryoshka sayesinde her vektörün sadece ilk 512, 256 ya da 128 sayısını tutabiliyoruz. Ne kadar kaybediyoruz?",
        "router": "## 5. Sıfır-örnek yönlendirici\nSimetrik `task: classification` önekiyle, hiç eğitim verisi olmadan soruları sınıflandır.",
        "litert": "## 6. LiteRT\nAynı model, 165 MB'lık int4 dosya olarak. Vektörleri PyTorch'unkilere o kadar yakın ki PyTorch ile kurulan indeksi sorgulayabiliyor.",
        "app": "## 7. Web uygulaması\nColab'da FastAPI uygulamasını (LiteRT ile) başlatır ve bir bağlantı yazar. **Tarayıcı** modunu da dene: model doğrudan tarayıcında çalışır.",
        "end": "## Sırada ne var\n- Dokümanlar (Türkçe ve İngilizce): `docs/` klasörü ya da yayındaki site.\n- Demoyu ücretsiz yayınla: `uv run --group docs scripts/build_docs.py --with-demo` ve `site/` klasörünü GitHub Pages'te yayınla.\n- `data/istanbul.jsonl` dosyasına kendi yerlerini ekle ve defteri yeniden çalıştır.",
    },
}

ORDER = [("title", None), ("setup", SETUP), ("hello", HELLO), ("build", BUILD), ("search", SEARCH),
         ("eval", EVAL), ("router", ROUTER), ("litert", LITERT), ("app", APP), ("end", None)]


def cell(kind: str, source: str) -> dict:
    lines = source.splitlines(keepends=True)
    if kind == "markdown":
        return {"cell_type": "markdown", "metadata": {}, "source": lines}
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines}


for lang, text in TEXT.items():
    cells = []
    for key, code in ORDER:
        cells.append(cell("markdown", text[key]))
        if code:
            cells.append(cell("code", code))
    nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}, "accelerator": "GPU",
                       "colab": {"provenance": [], "gpuType": "T4"}}}
    out = ROOT / "notebooks" / f"nerede_{lang}.ipynb"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(out.relative_to(ROOT))
