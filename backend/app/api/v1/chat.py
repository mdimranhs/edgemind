import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_service
from app.core.rate_limit import concurrency_limiter, rate_limiter
from app.models.chat import ChatRequest
from app.models.response import ChatResponse
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    raw_request: Request,
    service: ChatService = Depends(get_chat_service),
):
    await rate_limiter.check(raw_request)

    if request.stream:
        async def stream_generator():
            async with concurrency_limiter:
                try:
                    async for chunk in service.chat_stream(request.session_id, request.messages):
                        data = json.dumps(
                            {"choices": [{"delta": {"content": chunk}}]},
                            ensure_ascii=False,
                        )
                        yield f"data: {data}\n\n"
                    yield "data: [DONE]\n\n"
                except HTTPException as exc:
                    error = json.dumps({"error": {"message": exc.detail}}, ensure_ascii=False)
                    yield f"event: error\ndata: {error}\n\n"
                except Exception as exc:
                    logger.warning("Streaming terminated after response started: %s", type(exc).__name__)
                    error = json.dumps({"error": {"message": "The response stream was interrupted."}})
                    yield f"event: error\ndata: {error}\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async with concurrency_limiter:
        reply = await service.chat(request.session_id, request.messages)
        return ChatResponse(session_id=request.session_id, reply=reply)

