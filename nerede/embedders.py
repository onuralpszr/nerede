"""One interface, three runtimes for the same EmbeddingGemma 2 vector space.

    torch      sentence-transformers, any device (cuda / xpu / mps / cpu)
    litert     LiteRT-LM, int4 QAT .litertlm file, 165 MB, no torch needed
    openvino   Intel CPU / GPU (/ NPU), converted from the torch model

Spec strings: "torch", "torch:xpu", "litert", "litert:gpu", "openvino:GPU".
Every embedder returns L2-normalized float32 vectors of shape (n, 768).
Heavy libraries are imported lazily so the serving image can skip torch.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

MODEL_ID = "google/embeddinggemma-2"
LITERT_REPO = "litert-community/embeddinggemma-2-text-270m-litert-lm"
LITERT_FILE = "embeddinggemma-2-text-270m.litertlm"
DIM = 768


def _normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def pick_torch_device() -> str:
    """NVIDIA and AMD (ROCm) both show up as "cuda" in PyTorch."""
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return "xpu"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _fix_xpu_vision_pooling() -> None:
    """torch 2.15 XPU: max(dim=...) on int64 tensors skips about a third of the elements, so the
    vision pooler counts the wrong grid width and fails on some photos. int32 is fine, so the pooler's
    position math runs in int32. See bench/README.md, draft issue 3."""
    from transformers.models.gemma4 import modeling_gemma4

    pooler = modeling_gemma4.Gemma4VisionPooler
    original = pooler._avg_pool_by_positions
    if getattr(original, "int32_positions", False):
        return

    def pool(self, hidden_states, pixel_position_ids, length):
        return original(self, hidden_states, pixel_position_ids.int(), length)

    pool.int32_positions = True
    pooler._avg_pool_by_positions = pool


class TorchEmbedder:
    def __init__(self, device: str | None = None, modalities: tuple[str, ...] = ("text",)):
        from sentence_transformers import SentenceTransformer

        self.device = device or pick_torch_device()
        if self.device.startswith("xpu") and "image" in modalities:
            _fix_xpu_vision_pooling()
        # Setting an encoder config to None skips loading it: text-only is 270M params, not 740M.
        config_kwargs = {}
        if "image" not in modalities:
            config_kwargs["vision_config"] = None
        if "audio" not in modalities:
            config_kwargs["audio_config"] = None
        self.model = SentenceTransformer(MODEL_ID, device=self.device, config_kwargs=config_kwargs)
        self.name = f"torch:{self.device}"

    def embed(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        return _normalize(self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True))

    def embed_images(self, paths: list[str], batch_size: int = 8) -> np.ndarray:
        """Needs modalities=("text", "image"). Media go in as dicts and get no task prompt."""
        return _normalize(self.model.encode([{"image": p} for p in paths], batch_size=batch_size,
                                            convert_to_numpy=True, show_progress_bar=len(paths) > 16))


class LiteRTEmbedder:
    def __init__(self, backend: str = "cpu", model_path: str | None = None):
        import litert_lm
        from huggingface_hub import hf_hub_download

        litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)
        path = model_path or os.environ.get("LITERT_MODEL") or hf_hub_download(LITERT_REPO, LITERT_FILE)
        be = litert_lm.Backend.GPU() if backend.lower() == "gpu" else litert_lm.Backend.CPU()
        self.engine = litert_lm.EmbeddingEngine(path, backend=be)
        self.name = f"litert:{backend.lower()}"

    def embed(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        out = self.engine.compute_embedding_batch(list(texts))
        return _normalize([r.embedding for r in out])


class OpenVINOEmbedder:
    """Static-shape OpenVINO IR, built once from the torch model and cached under models/openvino."""

    def __init__(self, device: str = "GPU", max_len: int = 256, cache_dir: str = "models/openvino"):
        import openvino as ov
        from transformers import AutoTokenizer

        self.max_len = max_len
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        xml = Path(cache_dir) / f"embeddinggemma-2-text-{max_len}.xml"
        if not xml.exists():
            self._export(xml)
        self.compiled = ov.Core().compile_model(str(xml), device.upper())
        self.name = f"openvino:{device.upper()}"

    def _export(self, xml: Path) -> None:
        import openvino as ov
        import torch
        from sentence_transformers import SentenceTransformer

        st = SentenceTransformer(MODEL_ID, device="cpu", model_kwargs={"dtype": torch.float32},
                                 config_kwargs={"vision_config": None, "audio_config": None})

        class TextOnly(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.st = st

            def forward(self, input_ids, attention_mask):
                return self.st({"input_ids": input_ids, "attention_mask": attention_mask})["sentence_embedding"]

        shape = [1, self.max_len]
        example = self.tokenizer(["hello"], padding="max_length", max_length=self.max_len, return_tensors="pt")
        with torch.no_grad():
            model = ov.convert_model(TextOnly().eval(),
                                     example_input=(example["input_ids"], example["attention_mask"]),
                                     input=[(shape, ov.Type.i64), (shape, ov.Type.i64)])
        xml.parent.mkdir(parents=True, exist_ok=True)
        ov.save_model(model, str(xml))

    def embed(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        out = []
        for text in texts:
            enc = self.tokenizer([text], padding="max_length", truncation=True,
                                 max_length=self.max_len, return_tensors="np")
            out.append(self.compiled((enc["input_ids"], enc["attention_mask"]))[0][0])
        return _normalize(out)


def get_embedder(spec: str | None = None, modalities: tuple[str, ...] = ("text",)):
    """Build an embedder from a spec like "litert:gpu". Defaults to $NEREDE_BACKEND or "torch"."""
    spec = spec or os.environ.get("NEREDE_BACKEND", "torch")
    kind, _, option = spec.partition(":")
    if kind == "torch":
        return TorchEmbedder(device=option or None, modalities=modalities)
    if kind == "litert":
        return LiteRTEmbedder(backend=option or "cpu")
    if kind == "openvino":
        return OpenVINOEmbedder(device=option or "GPU")
    raise ValueError(f"unknown backend {spec!r} (use torch, litert or openvino)")
