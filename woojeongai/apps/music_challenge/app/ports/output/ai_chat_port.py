from __future__ import annotations

from abc import ABC, abstractmethod


class AiChatPort(ABC):
    """연습 상담용 대화 모델. 제출물 채점(AIEvaluatorPort)과 달리 텍스트만 주고받는다."""

    @abstractmethod
    def generate(self, message: str) -> str:
        pass
