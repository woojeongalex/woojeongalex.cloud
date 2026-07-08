"""[Layer: Ports] 보컬 마에스트로 출력 Port — 자기소개 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.evaluation_dto import MaestroIntroduceQuery, MaestroIntroduceResponse


class MaestroPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: MaestroIntroduceQuery) -> MaestroIntroduceResponse:
        pass
