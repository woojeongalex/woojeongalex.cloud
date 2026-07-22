"""[Layer: Ports] 보컬 마에스트로 출력 Port — DB 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.evaluation_dto import (
    MaestroAnalyzeResultDto,
    MaestroIntroduceQuery,
    MaestroIntroduceResponse,
)


class MaestroPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: MaestroIntroduceQuery) -> MaestroIntroduceResponse:
        pass

    @abstractmethod
    async def save_analysis(
        self,
        user_id: int | None,
        input_source: str,
        file_name: str,
        duration_sec: int,
        catalog_song_id: str | None,
        mr_search_list_id: int | None,
        result: MaestroAnalyzeResultDto,
    ) -> int:
        """ai_vocal_analyses.id 반환."""
