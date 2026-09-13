FROM python:3.14-slim

WORKDIR /app

# Keep Hugging Face artifacts in a deterministic image layer. The embedder is
# downloaded during the build so a new instance never downloads it on /chat.
ENV HF_HOME=/opt/huggingface

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install dependencies (cached layer if requirements unchanged)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Use uvicorn with optimized settings for faster cold starts
# --timeout-keep-alive: Keep connections alive longer
# --workers 1: Single worker for free tier (saves memory)
# --timeout-graceful-shutdown 5: Faster shutdown on redeploy
CMD uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --limit-concurrency 4 \
    --timeout-keep-alive 75 \
    --timeout-graceful-shutdown 5
