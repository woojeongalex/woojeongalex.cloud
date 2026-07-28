from __future__ import annotations

from abc import ABC, abstractmethod


class SemanticRouterUseCase(ABC):
    @abstractmethod
    async def route(self, message: str) -> str:
        """질문의 의도를 분류해 그래프/온톨로지 질문이면 그래프 QA에게,
        코딩 질문이면 LangChain 코딩 엔진에게, 그 외에는 Gemini에게 답을 위임한다."""
        pass
