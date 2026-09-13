import asyncio

from app.core.config import settings
from app.interfaces.llm import BaseLLM
from app.providers.hf_api import HuggingFaceInferenceAPIProvider
from app.providers.huggingface_llm import HuggingFaceLLMProvider
from app.services.chat_service import ChatService
from app.services.llm import LLMService
from app.services.memory import SQLiteHistory
from app.services.rag import RagService
from app.services.web_search import WebSearchService


_provider: BaseLLM | None = None
_rag_service: RagService | None = None
_memory: SQLiteHistory | None = None
_web_search: WebSearchService | None = None
_ready = False


def _create_provider() -> BaseLLM:
    if settings.llm_provider == "hf_api":
        return HuggingFaceInferenceAPIProvider()
    return HuggingFaceLLMProvider()


def init_services() -> None:
    """Eagerly initialize all services at startup (not lazily per request).

    Called from the app lifespan warmup so the expensive embedder download,
    FAISS RAG index, memory and LLM provider are ready before the first
    request — moving the cold-start cost out of /chat.
    """
    global _provider, _rag_service, _memory, _web_search

    if _provider is None:
        _provider = _create_provider()
        if isinstance(_provider, HuggingFaceLLMProvider):
            _provider.load()

    if _rag_service is None:
        _rag_service = RagService()

    if _memory is None:
        _memory = SQLiteHistory()

    if _web_search is None:
        _web_search = WebSearchService(enabled=settings.web_search_enabled)


async def warm_provider() -> None:
    """Fire a minimal request through the LLM provider so its telemetry,
    connection pool and any server-side model replica stay warm."""
    global _provider
    if _provider is None:
        init_services()
    if _provider is None or not hasattr(_provider, "warm"):
        return
    try:
        await asyncio.wait_for(_provider.warm(), timeout=30)
    except Exception:
        # A failed provider preflight means the service is not ready to accept
        # chat traffic. Let the lifespan fail instead of returning slow 502s.
        raise


async def initialize_for_startup() -> None:
    """Fully prepare the process before FastAPI accepts requests."""
    global _ready
    _ready = False
    init_services()
    if _rag_service is not None:
        # Encoding documents is CPU-bound; do not block the event loop while
        # the application lifespan performs this one-time startup work.
        await asyncio.to_thread(_rag_service.ingest)
    await warm_provider()
    _ready = True


def is_ready() -> bool:
    """Return whether RAG and provider warmup completed successfully."""
    return _ready


def get_chat_service() -> ChatService:
    """Return a fully-initialized ChatService (initialized at startup)."""
    global _provider, _rag_service, _memory, _web_search

    if all(v is not None for v in (_provider, _rag_service, _memory, _web_search)):
        return ChatService(
            llm_service=LLMService(provider=_provider),
            rag_service=_rag_service,
            memory=_memory,
            web_search=_web_search,
        )

    # Fallback: initialized anyway if warmup didn't run (e.g. tests)
    init_services()

    return ChatService(
        llm_service=LLMService(provider=_provider),
        rag_service=_rag_service,
        memory=_memory,
        web_search=_web_search,
    )
