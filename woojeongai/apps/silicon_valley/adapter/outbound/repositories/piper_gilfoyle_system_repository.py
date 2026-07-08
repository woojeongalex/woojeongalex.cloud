from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemQuery, GilfoyleSystemResponse
from silicon_valley.app.ports.output.piper_gilfoyle_system_port import GilfoyleSystemPort

logger = logging.getLogger(__name__)


class GilfoyleSystemRepository(GilfoyleSystemPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: GilfoyleSystemQuery) -> GilfoyleSystemResponse:
        logger.info(f"[GilfoyleSystemRepository] introduce_myself 진입 | request_data={query}")

        response: GilfoyleSystemResponse = GilfoyleSystemResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
        return response
