"""[Layer: Ports] 보컬 평가 입력 Port — 저장 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.vocal_mia_recorder_schema import MiaIntroduceSchema, MiaIntroduceResponse
from music.app.dtos.evaluation_dto import (
    VocalEvaluationCreateCommand,
    VocalEvaluationResultDto,
)


class EvaluationUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: MiaIntroduceSchema) -> MiaIntroduceResponse:
        pass

    @abstractmethod
    async def upload(
        self, command: VocalEvaluationCreateCommand
    ) -> VocalEvaluationResultDto:
        pass
