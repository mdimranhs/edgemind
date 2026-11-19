from collections.abc import AsyncGenerator
import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from starlette.requests import Request

from app.api.v1.chat import chat
from app.interfaces.llm import BaseLLM
from app.models.chat import ChatMessage
from app.models.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.llm import LLMService
from app.services.rag import RagService


class MockProvider(BaseLLM):
    async def generate(self, messages: list[ChatMessage]) -> str:
        return "Mock response for test"

    async def generate_stream(self, messages: list[ChatMessage]) -> AsyncGenerator[str, None]:
        for token in ["Mock", " ", "stream"]:
            yield token


class FakeEmbeddingModel:
    def encode(self, texts, show_progress_bar=False):
        return [[float(len(text) % 5 + 1), float(text.count("a") + 1), 1.0] for text in texts]


class ApiAndRagTests(unittest.TestCase):
    def test_rag_retrieval_and_source_attribution(self) -> None:
        rag = RagService(model=FakeEmbeddingModel())
        rag.ingest()
        self.assertGreater(len(rag.chunks), 0)
        self.assertIsNotNone(rag.chunk_embeddings)

        results = rag.retrieve("Who is Imran?", top_k=2)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertTrue(r.startswith("[Source: "))

    def test_rag_mmr_uses_cached_embeddings(self) -> None:
        rag = RagService(model=FakeEmbeddingModel())
        rag.ingest()
        # Mock model.encode to make sure it's only called ONCE for the query, not in _mmr loop
        encode_call_count = 0

        def counting_encode(*args, **kwargs):
            nonlocal encode_call_count
            encode_call_count += 1
            return FakeEmbeddingModel().encode(*args, **kwargs)

        rag.model.encode = counting_encode
        rag.retrieve("Tell me about Imran's background", top_k=3)

        # encode should only be called 1 time (for the query vector), not during MMR
        self.assertEqual(encode_call_count, 1)

    def test_chat_service_is_stateless_and_does_not_write_db(self) -> None:
        mock_provider = MockProvider()
        chat_service = ChatService(
            llm_service=LLMService(provider=mock_provider),
            rag_service=None,
            memory=None,
            web_search=None,
        )
        self.assertIsNone(chat_service._memory)

    def _test_request(self) -> Request:
        return Request({
            "type": "http",
            "method": "POST",
            "path": "/chat",
            "headers": [],
            "client": ("198.51.100.4", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
            "query_string": b"",
        })

    def test_chat_non_streaming_success(self) -> None:
        mock_service = ChatService(
            llm_service=LLMService(provider=MockProvider()),
            rag_service=None,
            memory=None,
            web_search=None,
        )
        response = asyncio.run(chat(
            ChatRequest(messages=[ChatMessage(role="user", content="Hello Imran")]),
            self._test_request(),
            service=mock_service,
        ))
        self.assertEqual(response.reply, "Mock response for test")

    def test_rate_limiter_ignores_spoofed_forwarding_headers(self) -> None:
        from app.core.rate_limit import InMemoryRateLimiter
        request = Request({
            "type": "http",
            "method": "POST",
            "path": "/chat",
            "headers": [(b"x-forwarded-for", b"203.0.113.7")],
            "client": ("198.51.100.4", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
            "query_string": b"",
        })
        limiter = InMemoryRateLimiter()
        self.assertEqual(limiter._extract_ip(request), "198.51.100.4")

    def test_chat_streaming_success(self) -> None:
        mock_service = ChatService(
            llm_service=LLMService(provider=MockProvider()),
            rag_service=None,
            memory=None,
            web_search=None,
        )
        response = asyncio.run(chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="Hello")], stream=True,
            ),
            self._test_request(),
            service=mock_service,
        ))

        async def read_stream() -> str:
            return "".join([chunk async for chunk in response.body_iterator])

        self.assertEqual(asyncio.run(read_stream()),
            'data: {"choices": [{"delta": {"content": "Mock"}}]}\n\n'
            'data: {"choices": [{"delta": {"content": " "}}]}\n\n'
            'data: {"choices": [{"delta": {"content": "stream"}}]}\n\n'
            'data: [DONE]\n\n',
        )


if __name__ == "__main__":
    unittest.main()

