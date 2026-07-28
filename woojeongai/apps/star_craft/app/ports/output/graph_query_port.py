from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GraphQueryPort(ABC):
    @abstractmethod
    async def find_recent_classifications(self, limit: int) -> list[dict[str, Any]]:
        """최근 분류·수집된 노드 목록을 그래프 DB에서 조회하는 추상 메소드"""
        pass
