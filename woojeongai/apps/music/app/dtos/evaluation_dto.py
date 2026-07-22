"""[Layer: Use Cases] 보컬 평가 DTO."""
from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "VocalEvaluationCreateCommand",
    "VocalEvaluationResultDto",
    "MiaIntroduceQuery",
    "MiaIntroduceResponse",
    "MaestroIntroduceQuery",
    "MaestroIntroduceResponse",
    "MaestroAnalyzeCommand",
    "MaestroAnalyzeResultDto",
]


@dataclass(frozen=True)
class MiaIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MiaIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class MaestroIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MaestroIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class MaestroAnalyzeCommand:
    audio_bytes: bytes
    content_type: str
    user_id: int | None
    input_source: str          # "mic" | "video"
    file_name: str
    duration_sec: int
    catalog_song_id: str | None
    mr_search_list_id: int | None


@dataclass(frozen=True)
class MaestroAnalyzeResultDto:
    analysis_id: int
    pitch_score: int
    rhythm_score: int
    vocal_grade: str
    summary: str
    mean_hz: float
    std_hz: float
    tempo: float
    duration: float


@dataclass(frozen=True)
class VocalEvaluationCreateCommand:
    pitch_score: int
    rhythm_score: int
    vocal_grade: str
    summary: str
    catalog_song_id: str | None
    mr_search_list_id: int | None
    input_source: str
    file_name: str
    duration_sec: int


@dataclass(frozen=True)
class VocalEvaluationResultDto:
    id: int
    ok: bool = True
    message: str = "저장되었습니다."
