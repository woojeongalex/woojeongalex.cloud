import requests
from fastapi import APIRouter, Depends, HTTPException

from silicon_valley.adapter.inbound.api.schemas.piper_hendricks__ceo_chat_schema import (
    HendricksChatRequest,
    HendricksChatResponse,
)
from silicon_valley.adapter.inbound.api.schemas.piper_hendricks__ceo_schema import (
    HendricksCeoSchema,
)
from silicon_valley.app.dtos.piper_hendricks__ceo_dto import HendricksCeoResponse
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import (
    HendricksCeoUseCase,
)
from silicon_valley.dependencies.piper_hendricks__ceo_provider import (
    get_hendricks_ceo_use_case,
)

"""
리처드 헨드릭스 (Richard Hendricks)
파이드 파이퍼의 CEO이자 창업자. 천재 개발자로 중간값 압축 알고리즘을 개발했지만 사회성은 부족한 인물.
"""
hendricks_ceo_router = APIRouter(prefix="/hendricks", tags=["hendricks"])


@hendricks_ceo_router.get("/myself")
async def introduce_myself(
    hendricks: HendricksCeoUseCase = Depends(get_hendricks_ceo_use_case),
) -> HendricksCeoResponse:
    return await hendricks.introduce_myself(
        HendricksCeoSchema(id=5, name="리처드 헨드릭스 (Richard Hendricks)")
    )


@hendricks_ceo_router.post("/chat")
async def chat(
    request: HendricksChatRequest,
    hendricks: HendricksCeoUseCase = Depends(get_hendricks_ceo_use_case),
) -> HendricksChatResponse:
    try:
        reply = await hendricks.chat(request.message)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"로컬 LLM 호출 실패: {e}") from e
    return HendricksChatResponse(reply=reply)
