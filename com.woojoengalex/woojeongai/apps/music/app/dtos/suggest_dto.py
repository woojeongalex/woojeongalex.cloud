"""[Layer: Use Cases] Muse 보컬 추천 DTO."""
from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AiVocalAnalysisDto",
    "MuseIntroduceQuery",
    "MuseIntroduceResponse",
    "SingEvaluationDto",
    "VocalRecommendationCreateCommand",
    "VocalRecommendationResultDto",
    "VocalRecommendationSaveCommand",
]


@dataclass(frozen=True)
class MuseIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MuseIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class SingEvaluationDto:
    id: int


@dataclass(frozen=True)
class AiVocalAnalysisDto:
    id: int
    pitch_score: int
    rhythm_score: int
    vocal_grade: str
    summary: str | None


@dataclass(frozen=True)
class VocalRecommendationCreateCommand:
    sing_evaluation_id: int


@dataclass(frozen=True)
class VocalRecommendationSaveCommand:
    sing_evaluation_id: int
    ai_vocal_analysis_id: int
    vocalization_pattern: str
    recommended_genres: list[str]
    recommended_songs: list[str]


@dataclass(frozen=True)
class VocalRecommendationResultDto:
    id: int
    sing_evaluation_id: int
    pitch_score_snapshot: int
    rhythm_score_snapshot: int
    vocal_grade_snapshot: str
    vocalization_pattern: str
    recommended_genres: list[str]
    recommended_songs: list[str]
