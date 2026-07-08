"""[Layer: Use Cases] Cicero/Herald 스피치 평가 DTO."""
from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "CiceroIntroduceQuery",
    "CiceroIntroduceResponse",
    "HeraldIntroduceQuery",
    "HeraldIntroduceResponse",
    "OracleIntroduceQuery",
    "OracleIntroduceResponse",
    "SpeechEvaluationCreateCommand",
    "SpeechEvaluationResultDto",
    "SpeechTopicHitDto",
    "SpeechTopicsResultDto",
]


@dataclass(frozen=True)
class CiceroIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class CiceroIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class HeraldIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class HeraldIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class OracleIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class OracleIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class SpeechTopicHitDto:
    topic_id: str
    label: str
    description: str


@dataclass(frozen=True)
class SpeechTopicsResultDto:
    hits: list[SpeechTopicHitDto]
    count: int


@dataclass(frozen=True)
class SpeechEvaluationCreateCommand:
    topic_id: str
    clarity_score: int
    pace_score: int
    tone_score: int
    summary: str
    feedback_points: list[str]
    file_name: str
    duration_sec: int


@dataclass(frozen=True)
class SpeechEvaluationResultDto:
    id: int
    ok: bool = True
    message: str = "저장되었습니다."
