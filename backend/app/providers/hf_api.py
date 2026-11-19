import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import HTTPException, status
import httpx
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import HfHubHTTPError

from app.core.config import settings
from app.interfaces.llm import BaseLLM
from app.models.chat import ChatMessage

logger = logging.getLogger(__name__)


def _handle_provider_error(exc: Exception) -> HTTPException:
    if isinstance(exc, (asyncio.TimeoutError, httpx.TimeoutException)):
        logger.warning("Upstream inference timeout: %s", exc)
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Inference provider request timed out after {settings.hf_request_timeout}s.",
        )
    if isinstance(exc, HfHubHTTPError):
        code = getattr(exc.response, "status_code", 502) if hasattr(exc, "response") else 502
        if code == 429:
            logger.warning("Upstream rate limit reached: %s", exc)
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Upstream AI provider rate limit reached. Please wait a moment before trying again.",
            )
        if code == 503:
            logger.warning("Upstream model loading (503): %s", exc)
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model is currently warming up on provider. Please retry in 10-20 seconds.",
            )
        logger.error("Upstream HfHubHTTPError (%s): %s", code, exc)
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error communicating with upstream AI provider.",
        )
    if isinstance(exc, httpx.HTTPError):
        logger.error("Upstream HTTP error: %s", exc)
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Network error communicating with AI provider.",
        )
    logger.error("Unexpected error during inference: %s", exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An error occurred while generating response.",
    )


class HuggingFaceInferenceAPIProvider(BaseLLM):

    def __init__(self) -> None:
        self.model_id = settings.hf_model
        self.client = AsyncInferenceClient(
            token=settings.hf_token or None,
            timeout=settings.hf_request_timeout,
        )

    async def warm(self) -> None:
        """Send a tiny request to keep the model loaded on the provider."""
        try:
            await self.client.chat_completion(
                messages=[{"role": "user", "content": "ok"}],
                model=self.model_id,
                max_tokens=1,
            )
        except Exception as exc:
            logger.debug("Model warmup request failed: %s", exc)

    async def generate(self, messages: list[ChatMessage]) -> str:
        try:
            result = await self.client.chat_completion(
                messages=[{"role": m.role, "content": m.content} for m in messages],
                model=self.model_id,
                max_tokens=settings.max_generation_tokens,
                temperature=0.7,
                top_p=0.9,
                extra_body={"enable_thinking": False},
            )
            return result.choices[0].message.content or ""
        except Exception as exc:
            raise _handle_provider_error(exc) from exc

    async def generate_stream(
        self, messages: list[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat_completion(
                messages=[{"role": m.role, "content": m.content} for m in messages],
                model=self.model_id,
                max_tokens=settings.max_generation_tokens,
                temperature=0.7,
                top_p=0.9,
                stream=True,
                extra_body={"enable_thinking": False},
            )
        except Exception as exc:
            raise _handle_provider_error(exc) from exc

        try:
            async for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                if token:
                    yield token
        except Exception as exc:
            logger.warning("Streaming interrupted by upstream provider: %s", exc)
            raise _handle_provider_error(exc) from exc

