from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.instrument_fletcher_tuner_schema import FletcherIntroduceSchema, FletcherIntroduceResponse
from music.app.dtos.instrument_dto import FletcherIntroduceQuery
from music.app.ports.input.instrument_fletcher_tuner_use_case import FletcherTunerUseCase
from music.app.ports.output.instrument_fletcher_tuner_port import FletcherPort

logger = logging.getLogger(__name__)


class FletcherTunerInteractor(FletcherTunerUseCase):
    def __init__(self, repository: FletcherPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: FletcherIntroduceSchema) -> FletcherIntroduceResponse:
        return await self.repository.introduce_myself(FletcherIntroduceQuery(id=schema.id, name=schema.name))
