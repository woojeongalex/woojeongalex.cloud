from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.app.dtos.piper_hendricks__ceo_dto import HendricksCeoQuery, HendricksCeoResponse
from silicon_valley.app.ports.output.piper_hendricks__ceo_port import HendricksCeoPort

logger = logging.getLogger(__name__)


class HendricksCeoRepository(HendricksCeoPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: HendricksCeoQuery) -> HendricksCeoResponse:
        logger.info(f"[HendricksCeoRepository] introduce_myself 진입 | request_data={query}")

        response: HendricksCeoResponse = HendricksCeoResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
        return response
