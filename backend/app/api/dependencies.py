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


def _create_provider() -> BaseLLM:
    if settings.llm_provider == "hf_api":
        return HuggingFaceInferenceAPIProvider()
    return HuggingFaceLLMProvider()


def get_chat_service() -> ChatService:
    """Lazy-load services only when needed, not at startup."""
    global _provider, _rag_service, _memory, _web_search

    # Provider initialization (lightweight for hf_api)
    if _provider is None:
        _provider = _create_provider()
        # Only load model if using local provider (heavy operation)
        if isinstance(_provider, HuggingFaceLLMProvider):
            _provider.load()

    # Defer RAG ingestion - load on first chat request, not startup
    if _rag_service is None:
        _rag_service = RagService()
        # NOTE: Moved ingest() to background task - see main.py

    # Memory is lightweight, init immediately
    if _memory is None:
        _memory = SQLiteHistory()

    # Web search is lazy by design
    if _web_search is None:
        _web_search = WebSearchService(enabled=settings.web_search_enabled)

    return ChatService(
        llm_service=LLMService(provider=_provider),
        rag_service=_rag_service,
        memory=_memory,
        web_search=_web_search,
    )
