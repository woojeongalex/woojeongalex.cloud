from __future__ import annotations

from abc import ABC, abstractmethod


class GraphClassificationPort(ABC):
    @abstractmethod
    async def save_classification(
        self, filename: str, label: str, confidence: float
    ) -> str:
        """분류 결과를 그래프 DB에 노드로 저장하고 node_id를 반환한다."""
        pass
