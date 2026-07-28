from __future__ import annotations

from abc import ABC, abstractmethod


class GraphQaUseCase(ABC):
    @abstractmethod
    async def answer(self, message: str) -> str:
        """그래프 DB에 저장된 분류·수집 데이터를 조회해 자연어로 답하는 메소드"""
        pass
