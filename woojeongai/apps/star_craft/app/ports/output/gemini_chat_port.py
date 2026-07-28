from __future__ import annotations

from abc import ABC, abstractmethod


class GeminiChatPort(ABC):
    @abstractmethod
    def generate(self, message: str) -> str:
        """Gemini로 자유 형식 질문에 답하는 레포지토리 추상 메소드"""
        pass
