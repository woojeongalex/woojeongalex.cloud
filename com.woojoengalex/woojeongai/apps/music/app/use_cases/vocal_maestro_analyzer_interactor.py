from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import MaestroIntroduceSchema, MaestroIntroduceResponse
from music.app.dtos.evaluation_dto import MaestroIntroduceQuery
from music.app.ports.input.vocal_maestro_analyzer_use_case import MaestroAnalyzerUseCase
from music.app.ports.output.vocal_maestro_analyzer_port import MaestroPort

logger = logging.getLogger(__name__)


class MaestroAnalyzerInteractor(MaestroAnalyzerUseCase):
    def __init__(self, repository: MaestroPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: MaestroIntroduceSchema) -> MaestroIntroduceResponse:
        return await self.repository.introduce_myself(MaestroIntroduceQuery(id=schema.id, name=schema.name))
