"""[Layer: Ports] 보컬 평가 출력 Port — 3NF 번들 저장 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.evaluation_dto import MiaIntroduceQuery, MiaIntroduceResponse, VocalEvaluationCreateCommand, VocalEvaluationResultDto


class EvaluationPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: MiaIntroduceQuery) -> MiaIntroduceResponse:
        pass

    @abstractmethod
    async def save_evaluation_bundle(
        self, command: VocalEvaluationCreateCommand
    ) -> VocalEvaluationResultDto:
        pass
