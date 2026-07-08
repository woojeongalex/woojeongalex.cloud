import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Body

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.dependencies.crew_smith_captain_provider import get_smith_captain_use_case
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse

logger = logging.getLogger("titanic_flow_log")

smith_captain_router = APIRouter(prefix="/smith", tags=["smith"])


@smith_captain_router.post("/chat")
async def chat(
    schema: Annotated[ChatSchema, Body()],
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case),
) -> SmithCaptainResponse:
    
    logger.info("[Smith Chat] 사용자 입력: %s", schema.messages)
    return await smith.chat(schema)


@smith_captain_router.get("/myself")
async def introduce_myself(
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case),
):
    return await smith.introduce_myself(
        SmithCaptainSchema(id=2, name="에드워드 존 스미스 (Captain Edward John Smith)", model_type="jack")
    )

