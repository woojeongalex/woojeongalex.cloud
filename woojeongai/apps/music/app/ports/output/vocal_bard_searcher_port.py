"""[Layer: Ports] MR 검색 목록 출력 Port — Neon/Postgres 저장 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.search_dto import BardIntroduceQuery, BardIntroduceResponse, SongMrHitDto, SongMrSearchSaveDto


class ListPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: BardIntroduceQuery) -> BardIntroduceResponse:
        pass

    @abstractmethod
    async def get_by_id(self, mr_id: int) -> SongMrHitDto | None:
        pass

    @abstractmethod
    async def search_catalog(self, query: str) -> list[SongMrHitDto]:
        """catalog_songs 테이블에서 키워드 검색 (DB 기반)."""
        pass

    @abstractmethod
    async def save_search_results(
        self, items: list[SongMrSearchSaveDto]
    ) -> list[SongMrHitDto]:
        pass
