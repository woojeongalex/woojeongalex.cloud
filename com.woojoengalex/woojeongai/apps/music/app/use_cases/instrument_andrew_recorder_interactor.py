from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.instrument_andrew_recorder_schema import AndrewIntroduceSchema, AndrewIntroduceResponse
from music.app.dtos.instrument_dto import AndrewIntroduceQuery, InstrumentEvaluationCreateCommand, InstrumentEvaluationResultDto
from music.app.ports.input.instrument_andrew_recorder_use_case import InstrumentEvaluationUseCase
from music.app.ports.output.instrument_andrew_recorder_port import InstrumentPort

logger = logging.getLogger(__name__)


class AndrewRecorderInteractor(InstrumentEvaluationUseCase):
    def __init__(self, repository: InstrumentPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: AndrewIntroduceSchema) -> AndrewIntroduceResponse:
        return await self.repository.introduce_andrew(AndrewIntroduceQuery(id=schema.id, name=schema.name))

    async def upload(
        self, command: InstrumentEvaluationCreateCommand
    ) -> InstrumentEvaluationResultDto:
        result = await self.repository.save_evaluation_bundle(command)
        logger.info("[MUSIC][andrew][4/interactor] 저장 eval=%s", result.id)
        return result
