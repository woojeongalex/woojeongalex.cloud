from __future__ import annotations

from abc import ABC, abstractmethod


class LangchainChatUseCase(ABC):
    @abstractmethod
    async def chat(self, message: str) -> str:
        """LangChain 체인으로 코딩·기술 질문에 답하는 메소드"""
        pass
