from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_ruth_survivor_schema import RuthSurvivorSchema
from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorResponse
from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthSurvivorUseCase
from titanic.dependencies.passenger_ruth_survivor_provider import get_ruth_survivor_use_case

'''
루스 드윗 부카터 (Ruth DeWitt Bukater)
딸 로즈의 코르셋 끈을 강하게 조이며 상류층의 체면을 강요하던
통제욕의 상징. 1등석 승객(상류층) 조회를 담당한다.
'''

ruth_survivor_router = APIRouter(prefix="/ruth", tags=["ruth"])


@ruth_survivor_router.get("/myself")
async def introduce_myself(
    ruth: RuthSurvivorUseCase = Depends(get_ruth_survivor_use_case)
) -> RuthSurvivorResponse:
    return await ruth.introduce_myself(
        RuthSurvivorSchema(
            id=12,
            name="루스 드윗 부카터 (Ruth DeWitt Bukater)"
        )
    )
