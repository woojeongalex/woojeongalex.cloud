import logging

from fastapi import APIRouter, Depends, Query

from titanic.adapter.inbound.api.schemas.crew_walter_schema import WalterSchema
from titanic.adapter.inbound.api.schemas.titanic_schema import WalterPassengerPageResponse
from titanic.app.dtos.crew_walter_query import WalterResponse
from titanic.app.ports.input.crew_walter_use_case import WalterUseCase
from titanic.dependencies.crew_walter_provider import get_walter_use_case

logger = logging.getLogger(__name__)
walter_router = APIRouter(prefix="/walter", tags=["walter"])


@walter_router.get("/myself")
async def introduce_myself(
    walter: WalterUseCase = Depends(get_walter_use_case),
) -> WalterResponse:
    return await walter.introduce_myself(
        WalterSchema(id=6, name="월터 로드 (Walter Lord)")
    )


@walter_router.get("/passengers", response_model=WalterPassengerPageResponse)
async def read_passengers(
    source_file: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    walter: WalterUseCase = Depends(get_walter_use_case),
) -> WalterPassengerPageResponse:
    page_dto = await walter.read_passengers(source_file, page, size)
    return WalterPassengerPageResponse(
        source_file=page_dto.source_file,
        page=page_dto.page,
        size=page_dto.size,
        total=page_dto.total,
        total_pages=page_dto.total_pages,
        rows=page_dto.rows,
    )
