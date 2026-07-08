"""[Layer: Ports] 보컬 마에스트로 입력 Port — 자기소개 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import MaestroIntroduceSchema, MaestroIntroduceResponse


class MaestroAnalyzerUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: MaestroIntroduceSchema) -> MaestroIntroduceResponse:
        pass
