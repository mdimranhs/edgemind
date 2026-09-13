from collections.abc import AsyncGenerator

from huggingface_hub import AsyncInferenceClient

from app.core.config import settings
from app.interfaces.llm import BaseLLM
from app.models.chat import ChatMessage


class HuggingFaceInferenceAPIProvider(BaseLLM):

    def __init__(self) -> None:
        self.model_id = settings.hf_model
        self.client = AsyncInferenceClient(token=settings.hf_token or None)

    async def warm(self) -> None:
        """Send a tiny request to keep the model loaded on the provider."""
        await self.client.chat_completion(
            messages=[{"role": "user", "content": "ok"}],
            model=self.model_id,
            max_tokens=1,
        )

    async def generate(self, messages: list[ChatMessage]) -> str:
        result = await self.client.chat_completion(
            messages=[{"role": m.role, "content": m.content} for m in messages],
            model=self.model_id,
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
        )
        return result.choices[0].message.content

    async def generate_stream(
        self, messages: list[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        stream = await self.client.chat_completion(
            messages=[{"role": m.role, "content": m.content} for m in messages],
            model=self.model_id,
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
            stream=True,
        )
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                yield token
