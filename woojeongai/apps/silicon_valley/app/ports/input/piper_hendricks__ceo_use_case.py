from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from silicon_valley.app.dtos.piper_hendricks__ceo_dto import HendricksCeoResponse


class HendricksCeoUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, request: Any) -> HendricksCeoResponse:
        pass

    @abstractmethod
    async def get_company_status(self) -> dict[str, Any]:
        """리처드가 파이드 파이퍼의 현황을 반환하는 메소드"""
        return {}

    @abstractmethod
    async def chat(self, message: str) -> str:
        """로컬 LLM(EXAONE)으로 리처드 페르소나에 맞게 답하는 메소드"""
        pass
