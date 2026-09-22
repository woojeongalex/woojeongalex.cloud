from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from music_challenge.domain.value_objects.chart_vo import (
    InstrumentKind,
    LyricLine,
    MelodySource,
    Note,
)


class ChartStatus(str, Enum):
    EMPTY = "empty"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(frozen=True)
class ChallengeChart:
    """노래방·연주 화면의 악보.

    melody 는 정답을 뽑는 트랙(보컬 스템 또는 멜로디 악기 스템),
    backing 은 도전할 때 틀어 주는 반주 트랙이다.
    """

    challenge_id: int
    status: ChartStatus
    melody_source: MelodySource
    instrument: InstrumentKind | None
    notes: list[Note]
    duration: float | None
    melody_s3_key: str | None
    backing_s3_key: str | None
    lyric_lines: list[LyricLine]
    error: str | None
    updated_at: datetime
