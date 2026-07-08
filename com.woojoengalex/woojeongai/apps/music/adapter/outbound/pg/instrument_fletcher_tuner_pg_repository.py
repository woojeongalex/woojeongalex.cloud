from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.app.dtos.instrument_dto import FletcherIntroduceQuery, FletcherIntroduceResponse
from music.app.ports.output.instrument_fletcher_tuner_port import FletcherPort

logger = logging.getLogger(__name__)


class FletcherTunerPgRepository(FletcherPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: FletcherIntroduceQuery) -> FletcherIntroduceResponse:
        logger.info("[MUSIC][fletcher][5/repository] introduce_myself name=%s", query.name)
        return FletcherIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
