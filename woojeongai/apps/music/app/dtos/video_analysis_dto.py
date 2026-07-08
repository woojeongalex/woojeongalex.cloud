"""[Layer: Use Cases] Lumiere 비디오 보컬 분석 DTO."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["LumiereIntroduceQuery", "LumiereIntroduceResponse", "VideoVocalAnalysisResultDto"]


@dataclass(frozen=True)
class LumiereIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class LumiereIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class VideoVocalAnalysisResultDto:
    pitch_data: dict[str, Any]
    bpm: float
    duration: float
    emotions: dict[str, float]
