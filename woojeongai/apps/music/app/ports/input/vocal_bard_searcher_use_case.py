"""[Layer: Ports] MR 검색 입력 Port — 검색·저장 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.vocal_bard_searcher_schema import BardIntroduceSchema, BardIntroduceResponse
from music.app.dtos.search_dto import SongMrSearchResultDto


class SearchUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: BardIntroduceSchema) -> BardIntroduceResponse:
        pass

    @abstractmethod
    async def search(self, raw_query: str) -> SongMrSearchResultDto:
        pass
