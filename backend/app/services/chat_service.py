import logging
from collections.abc import AsyncGenerator

from app.interfaces.memory import BaseMemory

logger = logging.getLogger(__name__)
from app.models.chat import ChatMessage
from app.services.context_manager import trim_history
from app.services.llm import LLMService
from app.services.rag import RagService
from app.services.web_search import WebSearchService


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
            chunks = self._rag.retrieve(query)
            if chunks:
                parts.append("Knowledge base:\n" + "\n\n".join(chunks))

        if self._web_search:
            results = await self._web_search.search(query)
            logger.info("Web search for %r returned %d results", query, len(results))
            if results:
                parts.append("Web search results:\n" + "\n\n".join(results))

        context_str = "\n\n---\n\n".join(parts) if parts else None
        logger.info("Web search context: %s chars", len(context_str) if context_str else 0)
        return context_str

    async def _build_conversation(
        self, session_id: str, messages: list[ChatMessage],
    ) -> list[ChatMessage]:
        stored = []
        if self._memory:
            stored = await self._memory.get_history(session_id)
        history = [ChatMessage(**m) for m in stored]
        return trim_history(history + messages)

    async def _save_turn(
        self, session_id: str, messages: list[ChatMessage], reply: str,
    ) -> None:
        if self._memory is None:
            return
        for m in messages:
            await self._memory.add(session_id, m.role, m.content)
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
