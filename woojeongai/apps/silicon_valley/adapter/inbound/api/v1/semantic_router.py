import requests
from fastapi import APIRouter, Depends, HTTPException

from silicon_valley.adapter.inbound.api.schemas.semantic_router_chat_schema import (
    SemanticChatRequest,
    SemanticChatResponse,
)
from silicon_valley.app.ports.input.semantic_router_use_case import (
    SemanticRouterUseCase,
)
from silicon_valley.dependencies.semantic_router_provider import (
    get_semantic_router_use_case,
)

"""
시멘틱 라우터 (의도 분류기)
질문을 임베딩해 음악 관련 의도인지 판단한다. 음악 관련이면 로컬 EXAONE
(리처드 헨드릭스 페르소나·RAG)이, 그 외 일반 질문은 Gemini가 답한다.
"""
semantic_chat_router = APIRouter(prefix="/chat", tags=["semantic-router"])


@semantic_chat_router.post("")
async def chat(
    request: SemanticChatRequest,
    router: SemanticRouterUseCase = Depends(get_semantic_router_use_case),
) -> SemanticChatResponse:
    try:
        reply = await router.route(request.message)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"모델 호출 실패: {e}") from e
    return SemanticChatResponse(reply=reply)
