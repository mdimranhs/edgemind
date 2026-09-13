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
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch==2.12.1+cpu && \
    pip install --no-cache-dir --only-binary :all: -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY backend/ .

# Copy the entrypoint script (uses exec form so SIGTERM reaches uvicorn directly)
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint script expands $PORT at runtime while keeping exec-form signal handling
CMD ["./docker-entrypoint.sh"]
