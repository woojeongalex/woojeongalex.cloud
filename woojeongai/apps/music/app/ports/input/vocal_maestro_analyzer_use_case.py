"""[Layer: Ports] 보컬 마에스트로 입력 Port."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import (
    MaestroAnalyzeResponse,
    MaestroIntroduceResponse,
    MaestroIntroduceSchema,
)
from music.app.dtos.evaluation_dto import MaestroAnalyzeCommand


class MaestroAnalyzerUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: MaestroIntroduceSchema) -> MaestroIntroduceResponse:
        pass

    @abstractmethod
    async def analyze_vocal(self, command: MaestroAnalyzeCommand) -> MaestroAnalyzeResponse:
        """오디오 bytes → librosa 분석 → DB 저장 → 결과 반환."""
