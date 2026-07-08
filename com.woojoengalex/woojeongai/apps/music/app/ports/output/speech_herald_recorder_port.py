"""[Layer: Ports] 스피치 평가 출력 Port — 3NF 번들 저장 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.speech_dto import (
    CiceroIntroduceQuery,
    CiceroIntroduceResponse,
    HeraldIntroduceQuery,
    HeraldIntroduceResponse,
    SpeechEvaluationCreateCommand,
    SpeechEvaluationResultDto,
)


class SpeechPort(ABC):
    @abstractmethod
    async def introduce_cicero(self, query: CiceroIntroduceQuery) -> CiceroIntroduceResponse:
        pass

    @abstractmethod
    async def introduce_herald(self, query: HeraldIntroduceQuery) -> HeraldIntroduceResponse:
        pass

    @abstractmethod
    async def save_evaluation_bundle(
        self, command: SpeechEvaluationCreateCommand
    ) -> SpeechEvaluationResultDto:
        pass
