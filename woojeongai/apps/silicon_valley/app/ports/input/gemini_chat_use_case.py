from __future__ import annotations

from abc import ABC, abstractmethod


class GeminiChatUseCase(ABC):
    @abstractmethod
    async def chat(self, message: str) -> str:
        """항상 Gemini로만 답한다 (의도 분류 없음)."""
        pass
