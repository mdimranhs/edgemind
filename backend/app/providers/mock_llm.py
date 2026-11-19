from collections.abc import AsyncGenerator

from app.interfaces.llm import BaseLLM
from app.models.chat import ChatMessage


class MockLLMProvider(BaseLLM):

    async def generate(self, messages: list[ChatMessage]) -> str:
        last = messages[-1] if messages else ChatMessage(role="user", content="")
        return (
            "Mock response from EdgeMind.\n\n"
            f"You said: {last.content}\n"
            f"Total messages: {len(messages)}"
        )

    async def generate_stream(
        self, messages: list[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        tokens = ["Mock", " ", "stream", " ", "response"]
        for token in tokens:
            yield token

