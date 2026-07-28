from __future__ import annotations

from abc import ABC, abstractmethod


class LangchainChatPort(ABC):
    @abstractmethod
    async def generate(self, message: str) -> str:
        """LangChain 체인을 실행해 답변을 생성하는 레포지토리 추상 메소드"""
        pass
