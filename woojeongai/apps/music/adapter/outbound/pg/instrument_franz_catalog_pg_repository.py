from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.app.dtos.instrument_dto import FranzIntroduceQuery, FranzIntroduceResponse
from music.app.ports.output.instrument_andrew_recorder_port import InstrumentPort

logger = logging.getLogger(__name__)


class FranzCatalogPgRepository(InstrumentPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_franz(self, query: FranzIntroduceQuery) -> FranzIntroduceResponse:
        logger.info("[MUSIC][franz][5/repository] introduce_myself name=%s", query.name)
        return FranzIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def introduce_andrew(self, query, ) -> object:
        raise NotImplementedError

    async def save_evaluation_bundle(self, command):  # type: ignore[override]
        raise NotImplementedError
