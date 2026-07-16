from fastapi import APIRouter, Depends, HTTPException

from silicon_valley.adapter.inbound.api.schemas.gemini_chat_schema import (
    GeminiChatRequest,
    GeminiChatResponse,
)
from silicon_valley.app.ports.input.gemini_chat_use_case import GeminiChatUseCase
from silicon_valley.dependencies.gemini_chat_provider import get_gemini_chat_use_case

"""
Gemini 전용 채팅 (의도 분류 없음) — 프론트엔드의 가요·뮤지컬 연습 Gemini
배너가 이 엔드포인트만 호출한다. API 키는 항상 Keymaker가 관리한다.
"""
gemini_chat_router = APIRouter(prefix="/gemini", tags=["gemini-chat"])


@gemini_chat_router.post("/chat")
async def chat(
    request: GeminiChatRequest,
    gemini: GeminiChatUseCase = Depends(get_gemini_chat_use_case),
) -> GeminiChatResponse:
    try:
        reply = await gemini.chat(request.message)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return GeminiChatResponse(reply=reply)
