"""[Layer: Ports] 악기 플레처 입력 Port — 자기소개 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.instrument_fletcher_tuner_schema import FletcherIntroduceSchema, FletcherIntroduceResponse


class FletcherTunerUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: FletcherIntroduceSchema) -> FletcherIntroduceResponse:
        pass
