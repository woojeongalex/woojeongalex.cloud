from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse
from titanic.app.ports.output.crew_smith_captain_port import SmithCaptainPort

logger = logging.getLogger(__name__)


class SmithCaptainRepository(SmithCaptainPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        logger.info(f"[SmithCaptainRepository] introduce_myself 진입 | request_data={query}")
        return SmithCaptainResponse(
            status="success",
            type="STATISTICS",
            message="나는 에드워드 스미스 선장이오. 타이타닉에 대해 무엇이든 물어보시오.",
        )

    async def chat(self, message: str) -> SmithCaptainResponse:
        return SmithCaptainResponse(
            status="success",
            type="STATISTICS",
            message=message,
        )
