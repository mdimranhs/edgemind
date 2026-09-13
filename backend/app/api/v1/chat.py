from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_service
from app.models.chat import ChatRequest
from app.models.response import ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])

@router.post("/chat")
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    if request.stream:
        return StreamingResponse(
            service.chat_stream(request.session_id, request.messages),
            media_type="text/event-stream",
        )
    reply = await service.chat(request.session_id, request.messages)
    return ChatResponse(session_id=request.session_id, reply=reply)
