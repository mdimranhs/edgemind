# Architecture

## Stack

- **Framework**: FastAPI (Python)
- **LLM (local)**: Qwen2.5-1.5B-Instruct via HuggingFace Transformers, GPU (GTX 1650 Ti, float16)
- **LLM (cloud)**: Qwen2.5-Coder-3B-Instruct via HuggingFace Inference API
- **Provider switch**: `LLM_PROVIDER=local` / `LLM_PROVIDER=hf_api`
- **Vector Store**: FAISS (in-memory, cosine similarity, IndexFlatIP)
- **Embeddings**: all-MiniLM-L6-v2 (Sentence Transformers)
- **Retrieval**: MMR diversification, score threshold (0.3), source attribution
- **Memory**: SQLite via aiosqlite (persistent per-session history)

## Layers

```
Client → FastAPI → ChatService → LLMService → HuggingFaceLLMProvider
                                → RagService  → FAISS index
                                → SQLiteHistory → chat_history.db
```

### API Layer (`api/v1/chat.py`)

Single POST `/chat` endpoint. Accepts `session_id`, `messages`, and `stream` flag. Returns JSON or `StreamingResponse` (SSE).

### Service Layer

| Service | Responsibility |
|---|---|
| `ChatService` | Orchestrator — coordinates memory, RAG, web search, and LLM |
| `LLMService` | Prepends system prompt via `PromptBuilder`, delegates to provider |
| `PromptBuilder` | Builds full message list with system prompt + optional context injection |
| `ContextManager` | `trim_history()` drops oldest non-system messages at ~4096 token budget |
| `RagService` | Ingests `knowledge/*.md`, chunks by `##` headers, embeds, retrieves with MMR + score threshold + source attribution |
| `SQLiteHistory` | Stores per-session conversation history in SQLite |
| `WebSearchService` | Optional web search via DuckDuckGo, injected alongside RAG context |

### Provider Layer

| Provider | Status |
|---|---|
| `HuggingFaceLLMProvider` | Active — local GPU inference with streaming |
| `OpenAILLMProvider` | Stub |
| `OllamaLLMProvider` | Stub |
| `MockLLMProvider` | Removed |

### Interfaces

- `BaseLLM` → `generate()` / `generate_stream()`
- `BaseMemory` → `add()` / `get_history()`

## Data Flow

```
1. POST /chat {session_id, messages, stream}
2. ChatService loads history from SQLiteHistory(session_id)
3. Appends new messages, trims via ContextManager.trim_history()
4. RagService.retrieve(last query) → top-k chunks (MMR, score threshold, source attribution)
5. WebSearchService.search(last query) → optional web results
6. PromptBuilder.build(history, context=rag_chunks + web_results) → full prompt
7. LLMService.generate(full prompt) → provider.generate()
8. ChatService saves assistant reply to SQLiteHistory
9. Return response (JSON or SSE stream)
```

## Knowledge Base

Located at `backend/knowledge/`:

- `profile.md` — Owner bio, background, specialties, communication style
- `skills.md` — Skill tiers and practical experience with each stack
- `projects.md` — Project summaries with problem, responsibilities, architecture, lessons learned
- `system_identity.md` — Assistant behavior, confidence, knowledge usage, and tone rules
- `philosophy.md` — Engineering philosophy and tradeoff style
- `coding_preferences.md` — Coding, architecture, API, testing, and deployment preferences
- `current_learning.md` — Current AI, cloud, backend, and architecture focus
- `goals.md` — Career direction and long-term goals
- `contact.md` — Public contact and hiring paths
- `edgemind.md` — Project description, architecture, features, deployment details
