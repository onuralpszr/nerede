# Troubleshooting

??? question "`uv run` downloads 5 GB of CUDA libraries"
    Default PyTorch on Linux is the CUDA build. This project makes the CPU build the default through the `cpu`
    dependency group. If you passed `--no-default-groups`, you get the CUDA build on purpose. See [Setup](setup.md).

??? question "`ValueError: Found 1 <|image|> tokens in the text but no images were passed`"
    A text contains a literal `<|image|>`, `<|video|>` or `<|audio|>` while the vision or audio encoder is loaded.
    Those are media placeholders. Escape them before embedding plain text, as `nerede/prompts.py` does.

??? question "Scores look fine but ranking is worse at 256d or 128d"
    Re-normalize after truncating a Matryoshka vector, and use the same size for queries and documents.

??? question "The task prefixes in the LiteRT docs look different"
    The LiteRT-LM page lists `task: search query | text:`, while the model card uses `task: search result | query:` and
    `title: … | text: …`. This workshop uses the model card format on every runtime, and the eval confirms it works with LiteRT.

??? question "OpenVINO: `Path '…onnx_data' … is outside the base directory`"
    OpenVINO refuses ONNX external data that is a symlink, which is how the Hugging Face cache stores it.
    Download with `hf download … --local-dir`, or convert from PyTorch like `OpenVINOEmbedder` does.

??? question "OpenVINO gives wrong vectors for the onnx-community ONNX file"
    On our machine, reading `model_fp16.onnx` directly in OpenVINO gave vectors far from PyTorch (cosine 0.6 to 0.8)
    while onnxruntime was fine. Converting from PyTorch gives exact results, so that is what `OpenVINOEmbedder` does.

??? question "`split_with_sizes` error when indexing photos on XPU"
    torch 2.15 XPU returns wrong values for `max(dim=...)` on int64 tensors, which breaks the vision pooler on
    some photos. `nerede.TorchEmbedder` works around it on XPU. If you call sentence-transformers directly,
    build photos on CPU or copy `_fix_xpu_vision_pooling` from `nerede/embedders.py`.

??? question "`curl localhost:8080` resets with rootless podman"
    `localhost` may resolve to IPv6 `::1`, which rootless podman does not forward. Use `127.0.0.1`.

??? question "Browser mode is slow or does not start"
    The first run downloads about 175 MB with WebGPU. Without WebGPU (check `chrome://gpu`) the page uses WASM with the
    fp16 model, about 543 MB, because the q4 and q8 files use `GatherBlockQuantized`, which the WASM backend lacks
    (`Could not find an implementation for GatherBlockQuantized`). On WebGPU, keep each batch under about 2,700 tokens.

??? question "LiteRT prints lots of log lines"
    `LiteRTEmbedder` sets the log level to ERROR. In your own code, call
    `litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)` before creating the engine.
