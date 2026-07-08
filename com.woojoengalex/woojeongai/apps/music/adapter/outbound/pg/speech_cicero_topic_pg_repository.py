from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.app.dtos.speech_dto import CiceroIntroduceQuery, CiceroIntroduceResponse
from music.app.ports.output.speech_herald_recorder_port import SpeechPort

logger = logging.getLogger(__name__)


class CiceroTopicPgRepository(SpeechPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_cicero(self, query: CiceroIntroduceQuery) -> CiceroIntroduceResponse:
        logger.info("[MUSIC][cicero][5/repository] introduce_myself name=%s", query.name)
        return CiceroIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def introduce_herald(self, query, ) -> object:
        raise NotImplementedError

    async def save_evaluation_bundle(self, command):  # type: ignore[override]
        raise NotImplementedError
