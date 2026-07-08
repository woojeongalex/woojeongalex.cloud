from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorQuery, RuthSurvivorResponse
from titanic.app.ports.output.passenger_ruth_survivor_port import RuthSurvivorPort

logger = logging.getLogger(__name__)


class RuthSurvivorRepository(RuthSurvivorPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: RuthSurvivorQuery) -> RuthSurvivorResponse:
        logger.info(f"[RuthSurvivorRepository] introduce_myself 진입 | request_data={query}")

        response: RuthSurvivorResponse = RuthSurvivorResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
        return response
