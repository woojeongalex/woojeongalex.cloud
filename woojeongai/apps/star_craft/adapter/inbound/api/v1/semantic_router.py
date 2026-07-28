import requests
from fastapi import APIRouter, Depends, HTTPException

from star_craft.adapter.inbound.api.schemas.semantic_router_chat_schema import (
    SemanticChatRequest,
    SemanticChatResponse,
)
from star_craft.app.ports.input.semantic_router_use_case import SemanticRouterUseCase
from star_craft.dependencies.semantic_router_provider import (
    get_semantic_router_use_case,
)

"""
시멘틱 라우터 (의도 분류기)
질문을 임베딩해 의도(그래프/온톨로지·일반·코딩)를 판단한다. 그래프/온톨로지
질문이면 Neo4j에 저장된 분류 데이터를 조회해 답하고, 코딩 질문이면 LangChain
코딩 엔진(로컬 EXAONE)이, 그 외 일반 질문은 Gemini가 답한다.
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
