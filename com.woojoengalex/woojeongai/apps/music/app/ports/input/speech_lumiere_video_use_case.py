"""[Layer: Ports] 비디오 보컬 분석 입력 Port — 바이트 분석 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.speech_lumiere_video_schema import LumiereIntroduceSchema, LumiereIntroduceResponse
from music.app.dtos.video_analysis_dto import VideoVocalAnalysisResultDto


class VideoAnalysisUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: LumiereIntroduceSchema) -> LumiereIntroduceResponse:
        pass

    @abstractmethod
    def analyze(
        self, data: bytes, original_filename: str
    ) -> VideoVocalAnalysisResultDto:
        pass
