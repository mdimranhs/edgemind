from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_service, is_ready, startup_error
from app.models.chat import ChatRequest
from app.models.response import ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])


def require_ready() -> None:
    """Keep first user requests from performing heavyweight initialization."""
    if not is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=startup_error() or "Service is warming up; retry shortly",
        )


@router.post("/chat")
async def chat(
    request: ChatRequest,
    _: None = Depends(require_ready),
    service: ChatService = Depends(get_chat_service),
):
    if request.stream:
        return StreamingResponse(
            service.chat_stream(request.session_id, request.messages),
            media_type="text/event-stream",
        )
    reply = await service.chat(request.session_id, request.messages)
    return ChatResponse(session_id=request.session_id, reply=reply)
