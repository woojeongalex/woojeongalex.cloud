from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.app.dtos.evaluation_dto import MaestroIntroduceQuery, MaestroIntroduceResponse
from music.app.ports.output.vocal_maestro_analyzer_port import MaestroPort

logger = logging.getLogger(__name__)


class MaestroAnalyzerPgRepository(MaestroPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: MaestroIntroduceQuery) -> MaestroIntroduceResponse:
        logger.info("[MUSIC][maestro][5/repository] introduce_myself name=%s", query.name)
        return MaestroIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
