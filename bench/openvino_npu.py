"""Try EmbeddingGemma 2 (text-only) on Intel CPU/GPU/NPU via OpenVINO, converted from PyTorch."""
import sys, time
import numpy as np, torch, openvino as ov
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

L = 128
st = SentenceTransformer("google/embeddinggemma-2", device="cpu",
                         config_kwargs={"vision_config": None, "audio_config": None},
                         model_kwargs={"dtype": torch.float32})
tok = AutoTokenizer.from_pretrained("google/embeddinggemma-2")

class TextEmbedder(torch.nn.Module):
    def __init__(self, st):
        super().__init__()
        self.st = st
    def forward(self, input_ids, attention_mask):
        return self.st({"input_ids": input_ids, "attention_mask": attention_mask})["sentence_embedding"]

texts = ["task: search result | query: where can I eat a fish sandwich?",
         "title: none | text: Balık ekmek, Eminönü'nde teknelerden satılan ızgara balık sandviçidir."]
ref = st.encode(texts)
enc = tok(texts, padding="max_length", max_length=L, return_tensors="pt")
with torch.no_grad():
    ovm = ov.convert_model(TextEmbedder(st).eval(), example_input=(enc["input_ids"][:1], enc["attention_mask"][:1]),
                           input=[([1, L], ov.Type.i64), ([1, L], ov.Type.i64)])
core = ov.Core()
for dev in sys.argv[1:] or ["CPU", "GPU", "NPU"]:
    try:
        t = time.time(); cm = core.compile_model(ovm, dev); ct = time.time() - t
        out = np.stack([cm((enc["input_ids"][i:i+1].numpy(), enc["attention_mask"][i:i+1].numpy()))[0][0] for i in range(2)])
        out /= np.linalg.norm(out, axis=1, keepdims=True)
        feed = (enc["input_ids"][:1].numpy(), enc["attention_mask"][:1].numpy())
        t = time.time(); [cm(feed) for _ in range(20)]; lat = (time.time() - t) / 20
        print(f"RESULT {dev}: compile {ct:.1f}s, {lat*1000:.1f} ms/query, cos vs torch {[round(float(a @ b), 4) for a, b in zip(out, ref)]}")
    except Exception as e:
        print(f"RESULT {dev}: FAILED", str(e)[-1500:])
