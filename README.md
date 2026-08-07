# EdgeMind 🧠

EdgeMind is a local AI assistant backend powered by FastAPI and HuggingFace Transformers. It runs a Qwen2.5-1.5B-Instruct model on GPU with streaming, RAG, and persistent conversation memory.

## Features

- **Local GPU inference** — Qwen2.5-1.5B-Instruct on GTX 1650 Ti (float16)
- **Streaming** — Token-by-token via Server-Sent Events
- **RAG** — FAISS + Sentence Transformers (all-MiniLM-L6-v2), MMR diversification, score threshold, source attribution
- **Conversation memory** — Per-session history persisted in SQLite
- **Modular providers** — Local HuggingFace GPU / Cloud HuggingFace Inference API
- **REST API** — Single `/chat` endpoint with dual JSON/SSE mode

## Tech Stack

- Python / FastAPI / Uvicorn
- HuggingFace Transformers / PyTorch
- FAISS / Sentence Transformers (all-MiniLM-L6-v2)
- SQLite (aiosqlite)
- NVIDIA GTX 1650 Ti (CUDA)

## Quickstart

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

```bash
# Non-streaming
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role":"user", "content":"Who is Md Imran Hossain?"}]}'

# Streaming
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role":"user", "content":"Hello"}], "stream": true}'
```

## Progress

| # | Milestone | Status |
|---|---|---|
| 1 | Base LLM integration (HuggingFace) | ✔ |
| 2 | Streaming token generation | ✔ |
| 3 | RAG with knowledge base | ✔ |
| 3a | RAG — MMR, score threshold, source attribution | ✔ |
| — | Conversation memory (SQLite) | ✔ |
| 4 | Fine-tune in Colab & deploy custom model | ⏸️ on hold |
