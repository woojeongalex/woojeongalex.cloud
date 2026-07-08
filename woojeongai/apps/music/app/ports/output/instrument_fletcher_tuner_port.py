"""[Layer: Ports] 악기 플레처 출력 Port — 자기소개 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.instrument_dto import FletcherIntroduceQuery, FletcherIntroduceResponse


class FletcherPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: FletcherIntroduceQuery) -> FletcherIntroduceResponse:
        pass
