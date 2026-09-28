from __future__ import annotations

from abc import ABC, abstractmethod


class AiChatUseCase(ABC):
    @abstractmethod
    async def chat(self, message: str) -> str:
        """연습·음정·박자 질문에 답한다."""
        pass
