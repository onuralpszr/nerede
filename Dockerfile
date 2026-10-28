# Nerede? serving image: FastAPI + LiteRT-LM (int4 QAT, 165 MB model), no torch.
# The index is built ahead of time with torch (workshop step 2) and shipped with the image.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/models \
    NEREDE_BACKEND=litert

WORKDIR /srv
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the model into the image so cold starts never hit Hugging Face.
RUN python -c "from huggingface_hub import hf_hub_download as d; \
d('litert-community/embeddinggemma-2-text-270m-litert-lm', 'embeddinggemma-2-text-270m.litertlm')"

# Model is in the image, never call the Hub at startup.
ENV HF_HUB_OFFLINE=1

COPY nerede/ nerede/
COPY data/ data/
COPY index/ index/
COPY app/ app/

# Cloud Run sets $PORT; default to 8080 locally.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
