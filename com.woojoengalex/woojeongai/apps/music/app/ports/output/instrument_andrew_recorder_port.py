"""[Layer: Ports] 악기 평가 출력 Port — 3NF 번들 저장 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.instrument_dto import (
    AndrewIntroduceQuery,
    AndrewIntroduceResponse,
    FranzIntroduceQuery,
    FranzIntroduceResponse,
    InstrumentEvaluationCreateCommand,
    InstrumentEvaluationResultDto,
)


class InstrumentPort(ABC):
    @abstractmethod
    async def introduce_franz(self, query: FranzIntroduceQuery) -> FranzIntroduceResponse:
        pass

    @abstractmethod
    async def introduce_andrew(self, query: AndrewIntroduceQuery) -> AndrewIntroduceResponse:
        pass

    @abstractmethod
    async def save_evaluation_bundle(
        self, command: InstrumentEvaluationCreateCommand
    ) -> InstrumentEvaluationResultDto:
        pass
