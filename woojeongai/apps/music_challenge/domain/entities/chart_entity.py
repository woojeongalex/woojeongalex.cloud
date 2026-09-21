from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from music_challenge.domain.value_objects.chart_vo import LyricLine, Note


class ChartStatus(str, Enum):
    EMPTY = "empty"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(frozen=True)
class ChallengeChart:
    challenge_id: int
    status: ChartStatus
    notes: list[Note]
    duration: float | None
    vocal_s3_key: str | None
    instrumental_s3_key: str | None
    lyric_lines: list[LyricLine]
    error: str | None
    updated_at: datetime
