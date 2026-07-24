# EdgeMind Project

Description:
EdgeMind is a local AI assistant backend built using FastAPI and HuggingFace Transformers. Deployed on Railway with a dual-provider architecture.

Features:
- Local GPU inference (GTX 1650 Ti, float16) via HuggingFaceLLMProvider
- Cloud inference via HuggingFace Inference API (AsyncInferenceClient)
- Streaming responses using TextIteratorStreamer
- Modular LLM provider architecture (switched via LLM_PROVIDER env var)
- Session-based chat system with SQLite persistence (aiosqlite)
- RAG with FAISS and Sentence Transformers (all-MiniLM-L6-v2)
- Conversation memory with context trimming (~4096 token budget)
- Knowledge base chunks by ## headers, top-3 retrieval

Architecture:
- FastAPI backend with Uvicorn
- LLM service abstraction layer (HuggingFaceLLMProvider + HuggingFaceInferenceAPIProvider)
- ChatService (orchestrator: memory → RAG → context trim → LLM)
- ContextManager (trim_history drops oldest non-system messages)
- RagService (FAISS IndexFlatIP, cosine similarity via normalized embeddings)
- SQLiteHistory per-session persistence

Default Model (local): Qwen/Qwen2.5-1.5B-Instruct
Cloud Model: Qwen/Qwen2.5-Coder-3B-Instruct (via HF Inference Providers)

Deployment:
- Railway (Dockerfile, python:3.14-slim)
- Dynamic PORT via ${PORT:-8000}
- Railway Project ID: 20af25af-82ab-49bb-8aca-fb97a8a2290e
- URL: https://fantastic-fascination-production-12dd.up.railway.app

Current State:
- Milestone 1: Base LLM integration ✔
- Milestone 2: Streaming implemented ✔
- Milestone 3: RAG implemented ✔
- Milestone 4: Fine-tuning (on hold)
