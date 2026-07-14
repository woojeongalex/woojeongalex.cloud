from __future__ import annotations

from abc import ABC, abstractmethod


class SongRagPort(ABC):
    @abstractmethod
    async def search_similar_songs(
        self, embedding: list[float], limit: int = 5
    ) -> list[dict[str, str | None]]:
        """embedding과 가장 가까운 catalog_songs 행을 반환한다."""
        pass
