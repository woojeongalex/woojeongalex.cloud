"""[Layer: Ports] 보컬 추천 입력 Port — 생성·조회 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.vocal_muse_recommender_schema import MuseIntroduceSchema, MuseIntroduceResponse
from music.app.dtos.suggest_dto import (
    VocalRecommendationCreateCommand,
    VocalRecommendationResultDto,
)


class SuggestUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: MuseIntroduceSchema) -> MuseIntroduceResponse:
        pass

    @abstractmethod
    async def upload(
        self, command: VocalRecommendationCreateCommand
    ) -> VocalRecommendationResultDto:
        pass

    @abstractmethod
    async def read(
        self, sing_evaluation_id: int
    ) -> VocalRecommendationResultDto | None:
        pass
