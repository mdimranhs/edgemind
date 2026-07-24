# Roadmap

## Completed

| Milestone | Description | Status |
|---|---|---|
| 1 | Replace MockLLMProvider with HuggingFaceLLMProvider (Qwen2.5-1.5B) | ✔ |
| 2 | Streaming token generation via TextIteratorStreamer + SSE | ✔ |
| 3 | RAG with FAISS + Sentence Transformers, knowledge/ ingestion | ✔ |
| 3a | RAG improvements — MMR, score threshold, source attribution | ✔ |
| — | Conversation memory with SQLite persistence | ✔ |
| — | Context control (token budget, history trimming via ContextManager) | ✔ |
| — | Railway deployment (Dockerfile, dual-provider cloud/local) | ✔ |
| — | Structured knowledge base → 2 files (imran-parthib.md, edgemind.md) | ✔ |

## Next

| Priority | Feature |
|---|---|
| Medium | Frontend (Next.js chat UI) |
| Medium | Tool calling (search, browse) |
| Low | Conversation memory expiry / TTL |

## On Hold

| Feature | Reason |
|---|---|
| Milestone 4: Fine-tune in Colab | High risk of regressing instruction-following. Only pursue as a research experiment with a curated dataset. RAG + prompting already cover personalization needs. |
