"""[Layer: Ports] 스피치 오라클 출력 Port — 자기소개 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.app.dtos.speech_dto import OracleIntroduceQuery, OracleIntroduceResponse


class OraclePort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: OracleIntroduceQuery) -> OracleIntroduceResponse:
        pass
