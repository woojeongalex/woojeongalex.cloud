"""Walter inbound — DTO ↔ HTTP 스키마 변환 (Adapter 경계 1회)."""

from titanic.adapter.inbound.api.schemas.titanic_schema import (
    WalterPassengerItem,
    WalterPassengerPageResponse,
)
from titanic.app.dtos.crew_walter_query import WalterPassengerPageDto


def walter_page_dto_to_response(page: WalterPassengerPageDto) -> WalterPassengerPageResponse:
    return WalterPassengerPageResponse(
        source_file=page.source_file,
        page=page.page,
        size=page.size,
        total=page.total,
        total_pages=page.total_pages,
        rows=[WalterPassengerItem(**row) for row in page.rows],
    )
