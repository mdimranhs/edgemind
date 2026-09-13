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


def init_services() -> None:
    """Initialize chat services on the first request that needs them."""
    global _provider, _rag_service, _memory, _web_search

    if _provider is None:
        _provider = _create_provider()
        if isinstance(_provider, HuggingFaceLLMProvider):
            _provider.load()

    if _rag_service is None:
        _rag_service = RagService()
        _rag_service.ingest()

    if _memory is None:
        _memory = SQLiteHistory()

    if _web_search is None:
        _web_search = WebSearchService(enabled=settings.web_search_enabled)


def get_chat_service() -> ChatService:
    """Return a fully-initialized ChatService."""
    global _provider, _rag_service, _memory, _web_search

    if all(v is not None for v in (_provider, _rag_service, _memory, _web_search)):
        return ChatService(
            llm_service=LLMService(provider=_provider),
            rag_service=_rag_service,
            memory=_memory,
            web_search=_web_search,
        )

    init_services()

    return ChatService(
        llm_service=LLMService(provider=_provider),
        rag_service=_rag_service,
        memory=_memory,
        web_search=_web_search,
    )
