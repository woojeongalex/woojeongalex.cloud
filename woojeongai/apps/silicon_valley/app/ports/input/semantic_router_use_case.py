from __future__ import annotations

from abc import ABC, abstractmethod


class SemanticRouterUseCase(ABC):
    @abstractmethod
    async def route(self, message: str) -> str:
        """질문의 의도를 분류해 음악 관련이면 헨드릭스(로컬 EXAONE)에게,
        그 외에는 Gemini에게 답을 위임한다."""
        pass
