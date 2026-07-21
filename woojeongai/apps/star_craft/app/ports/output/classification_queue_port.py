from __future__ import annotations

from abc import ABC, abstractmethod


class ClassificationQueuePort(ABC):
    @abstractmethod
    async def enqueue_post_process(self, node_id: str, label: str) -> str:
        """후처리 태스크를 큐에 적재하고 task_id를 반환한다."""
        pass
