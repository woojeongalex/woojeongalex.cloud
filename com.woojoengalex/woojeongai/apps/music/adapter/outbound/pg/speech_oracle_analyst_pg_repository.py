from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.app.dtos.speech_dto import OracleIntroduceQuery, OracleIntroduceResponse
from music.app.ports.output.speech_oracle_analyst_port import OraclePort

logger = logging.getLogger(__name__)


class OracleAnalystPgRepository(OraclePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: OracleIntroduceQuery) -> OracleIntroduceResponse:
        logger.info("[MUSIC][oracle][5/repository] introduce_myself name=%s", query.name)
        return OracleIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
