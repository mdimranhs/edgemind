# EdgeMind Architecture

EdgeMind is a standalone FastAPI service for portfolio and coding assistance. The Next.js portfolio calls the API over HTTP; the backend can also be run and integrated independently.

## Request flow

1. `POST /chat` validates the conversation, rejects client supplied system messages, applies per-process rate and concurrency limits, and assigns a request ID.
2. The chat service adds the server-owned system prompt, optional retrieved knowledge, and optional web search context.
3. `LLMService` routes generation to the configured local Hugging Face model, Hugging Face Inference API, or mock provider.
4. Non-streaming calls return a JSON reply. Streaming calls return OpenAI-compatible Server-Sent Events (`choices[0].delta.content`) followed by `data: [DONE]`.

## State and storage

Chat is stateless by default (`MEMORY_BACKEND=none`). The client sends the recent conversation turns with each request, so the service does not persist transcripts. An optional SQLite history backend is available for deployments that intentionally need server-side history (`MEMORY_BACKEND=sqlite`); it requires a persistent writable volume and is not suitable for ephemeral serverless filesystems.

Knowledge documents under `backend/knowledge` are chunked and embedded at startup. Sentence Transformers creates embeddings, and FAISS keeps the index in process memory. This index is rebuilt when an instance starts. The API currently has no shared external vector database, so each replica loads its own copy.

## Deployment considerations

- Configure `CORS_ALLOWED_ORIGINS` with the exact frontend origins in production.
- Set `HF_TOKEN` for Hugging Face Inference API access; keep it in the host's secret store.
- The rate limiter and concurrency semaphore are per process. Multiple replicas do not share limits.
- Configure trusted proxy handling at the deployment boundary. The rate limiter uses the ASGI peer address and does not trust arbitrary forwarded headers.
- Use a CPU/GPU host with enough memory for the selected local model, or select `LLM_PROVIDER=hf_api` to run inference remotely.
- `/health` reports process health; it does not promise that a remote model provider is reachable.

## Main components

| Component | Responsibility |
| --- | --- |
| `app/api/v1/chat.py` | Chat endpoint and JSON/SSE response formatting |
| `app/api/dependencies.py` | Constructs provider, retrieval, optional memory, and chat service |
| `app/services/chat_service.py` | Prompt assembly and orchestration |
| `app/services/rag.py` | Local knowledge ingestion, FAISS retrieval, and source attribution |
| `app/providers/` | Local, hosted Hugging Face, and mock model implementations |
| `app/core/rate_limit.py` | Per-process request and inference concurrency limits |

