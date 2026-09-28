from fastapi import APIRouter, Depends, HTTPException

from music_challenge.adapter.inbound.api.deps.music_challenge_deps import (
    get_ai_chat_use_case,
)
from music_challenge.adapter.inbound.api.schemas.ai_chat_schema import (
    AiChatRequest,
    AiChatResponse,
)
from music_challenge.app.ports.input.ai_chat_use_case import AiChatUseCase

"""홈 화면의 '연습이 막히면 대화로' 배너가 이 엔드포인트만 호출한다."""
ai_chat_router = APIRouter(prefix="/ai", tags=["ai-chat"])


@ai_chat_router.post("/chat")
async def chat(
    request: AiChatRequest,
    use_case: AiChatUseCase = Depends(get_ai_chat_use_case),
) -> AiChatResponse:
    try:
        reply = await use_case.chat(request.message)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return AiChatResponse(reply=reply)
