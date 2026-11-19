import logging
from collections.abc import AsyncGenerator

from app.core.config import settings
from app.interfaces.memory import BaseMemory
from app.models.chat import ChatMessage
from app.services.context_manager import trim_history
from app.services.llm import LLMService
from app.services.rag import RagService
from app.services.web_search import WebSearchService

logger = logging.getLogger(__name__)


class ChatService:

    def __init__(
        self,
        llm_service: LLMService,
        rag_service: RagService | None = None,
        memory: BaseMemory | None = None,
        web_search: WebSearchService | None = None,
    ) -> None:
        self._llm_service = llm_service
        self._rag = rag_service
        self._memory = memory
        self._web_search = web_search

    async def _retrieve_context(self, messages: list[ChatMessage]) -> str | None:
        query = messages[-1].content if messages else ""
        parts: list[str] = []

        if self._rag:
            chunks = self._rag.retrieve(query, top_k=settings.max_retrieved_chunks)
            if chunks:
                parts.append("Knowledge base:\n" + "\n\n".join(chunks))

        if self._web_search:
            results = await self._web_search.search(query)
            logger.info("Web search completed (%d results for query len %d)", len(results), len(query))
            if results:
                parts.append("Web search results:\n" + "\n\n".join(results))

        context_str = "\n\n---\n\n".join(parts) if parts else None
        return context_str

    async def _build_conversation(
        self, session_id: str, messages: list[ChatMessage],
    ) -> list[ChatMessage]:
        if self._memory is not None:
            stored = await self._memory.get_history(session_id)
            history = [ChatMessage(**m) for m in stored]
            # Persisted history already contains prior turns. Use only this
            # request's newest user turn to avoid replaying/saving duplicates.
            conversation = history + [messages[-1]]
        else:
            conversation = messages

        bounded = conversation[-settings.max_history_messages:] if conversation else []
        return trim_history(bounded, budget=settings.max_prompt_tokens)

    async def _save_turn(
        self, session_id: str, messages: list[ChatMessage], reply: str,
    ) -> None:
        if self._memory is None:
            return
        # Only save turns if an explicit persistent memory provider is configured
        await self._memory.add(session_id, "user", messages[-1].content)
        await self._memory.add(session_id, "assistant", reply)

    async def chat(
        self, session_id: str, messages: list[ChatMessage],
    ) -> str:
        full = await self._build_conversation(session_id, messages)
        context = await self._retrieve_context(full)
        reply = await self._llm_service.generate(full, context=context)
        await self._save_turn(session_id, messages, reply)
        return reply

    async def chat_stream(
        self, session_id: str, messages: list[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        full = await self._build_conversation(session_id, messages)
        context = await self._retrieve_context(full)
        reply_chunks: list[str] = []
        async for token in self._llm_service.generate_stream(full, context=context):
            reply_chunks.append(token)
            yield token
        reply = "".join(reply_chunks)
        await self._save_turn(session_id, messages, reply)

