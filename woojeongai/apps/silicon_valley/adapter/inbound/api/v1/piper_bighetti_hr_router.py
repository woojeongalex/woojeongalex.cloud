from fastapi import APIRouter, Depends

from silicon_valley.adapter.inbound.api.schemas.piper_bighetti_hr_schema import BighettiHrSchema
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse
from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from silicon_valley.dependencies.piper_bighetti_hr_provider import get_bighetti_hr_use_case

'''
넬슨 비게티 (Nelson Bighetti / Big Head)
리처드의 절친이자 파이드 파이퍼 공동 창업자. 실력보다 운으로 Hooli에서 승승장구하다 HR을 담당하게 된 인물.
'''
bighetti_hr_router = APIRouter(prefix="/bighetti", tags=["bighetti"])


@bighetti_hr_router.get("/myself")
async def introduce_myself(
    bighetti: BighettiHrUseCase = Depends(get_bighetti_hr_use_case)
) -> BighettiHrResponse:
    return await bighetti.introduce_myself(
        BighettiHrSchema(
            id=1,
            name="넬슨 비게티 (Nelson Bighetti)"
        )
    )
