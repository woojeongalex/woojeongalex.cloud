"""[Layer: Ports] 보컬 추천 출력 Port — 조회·저장 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.suggest_dto import (
    AiVocalAnalysisDto,
    MuseIntroduceQuery,
    MuseIntroduceResponse,
    SingEvaluationDto,
    VocalRecommendationResultDto,
    VocalRecommendationSaveCommand,
)


class SuggestPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: MuseIntroduceQuery) -> MuseIntroduceResponse:
        pass

    @abstractmethod
    async def get_sing_evaluation_by_id(
        self, evaluation_id: int
    ) -> SingEvaluationDto | None:
        pass

    @abstractmethod
    async def get_ai_analysis_for_sing_evaluation(
        self, sing_evaluation_id: int
    ) -> AiVocalAnalysisDto | None:
        pass

    @abstractmethod
    async def get_ai_analysis_by_id(
        self, ai_analysis_id: int
    ) -> AiVocalAnalysisDto | None:
        pass

    @abstractmethod
    async def save_recommendation(
        self, command: VocalRecommendationSaveCommand
    ) -> VocalRecommendationResultDto:
        pass

    @abstractmethod
    async def get_latest_by_evaluation_id(
        self, sing_evaluation_id: int
    ) -> VocalRecommendationResultDto | None:
        pass
