from fastapi import APIRouter, Depends

from silicon_valley.adapter.inbound.api.schemas.piper_gilfoyle_system_schema import GilfoyleSystemSchema
from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemResponse
from silicon_valley.app.ports.input.piper_gilfoyle_system_use_case import GilfoyleSystemUseCase
from silicon_valley.dependencies.piper_gilfoyle_system_provider import get_gilfoyle_system_use_case

'''
버트람 길포일 (Bertram Gilfoyle)
파이드 파이퍼의 시스템 아키텍트. 냉소적이고 능력 있으며 서버 인프라 전반을 담당하는 인물.
'''
gilfoyle_system_router = APIRouter(prefix="/gilfoyle", tags=["gilfoyle"])


@gilfoyle_system_router.get("/myself")
async def introduce_myself(
    gilfoyle: GilfoyleSystemUseCase = Depends(get_gilfoyle_system_use_case)
) -> GilfoyleSystemResponse:
    return await gilfoyle.introduce_myself(
        GilfoyleSystemSchema(
            id=4,
            name="버트람 길포일 (Bertram Gilfoyle)"
        )
    )
