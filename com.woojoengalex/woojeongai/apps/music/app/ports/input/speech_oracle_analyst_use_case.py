"""[Layer: Ports] 스피치 오라클 입력 Port — 자기소개 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.speech_oracle_analyst_schema import OracleIntroduceSchema, OracleIntroduceResponse


class OracleAnalystUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: OracleIntroduceSchema) -> OracleIntroduceResponse:
        pass
