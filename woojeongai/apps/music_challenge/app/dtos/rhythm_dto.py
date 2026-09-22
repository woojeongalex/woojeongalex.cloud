from dataclasses import dataclass
from datetime import datetime

from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.services.rhythm_scoring import Press
from music_challenge.domain.value_objects.rhythm_vo import RhythmDifficulty, RhythmNote


@dataclass(frozen=True)
class RhythmSheetSummary:
    keys: int
    difficulty: RhythmDifficulty
    level: int
    note_count: int


@dataclass(frozen=True)
class RhythmChartResult:
    challenge_id: int
    status: ChartStatus
    bpm: float | None
    duration: float | None
    # 게임에서 틀 원곡(서명 URL)
    audio_url: str | None
    sheets: list[RhythmSheetSummary]
    error: str | None


@dataclass(frozen=True)
class RhythmSheetResult:
    challenge_id: int
    keys: int
    difficulty: RhythmDifficulty
    level: int
    bpm: float | None
    duration: float | None
    audio_url: str | None
    notes: list[RhythmNote]


@dataclass(frozen=True)
class SubmitRhythmPlayCommand:
    challenge_id: int
    keys: int
    difficulty: RhythmDifficulty
    presses: list[Press]
    # 검증된 토큰의 username. 비로그인이면 None — 기록은 남기되 랭킹에는 오르지 않는다.
    username: str | None


@dataclass(frozen=True)
class RhythmPlayResult:
    score: int
    accuracy: float
    max_combo: int
    cool: int
    good: int
    bad: int
    miss: int
    rank: int | None
    best_score: int | None
    is_personal_best: bool


@dataclass(frozen=True)
class RhythmRankingEntry:
    rank: int
    nickname: str
    score: int
    accuracy: float
    max_combo: int
    achieved_at: datetime


@dataclass(frozen=True)
class RhythmStanding:
    rank: int
    best_score: int


@dataclass(frozen=True)
class RhythmChartBrief:
    """목록용 — 노트 없이 채보 요약만."""

    challenge_id: int
    bpm: float | None
    duration: float | None
    sheets: list[RhythmSheetSummary]


@dataclass(frozen=True)
class RhythmSongItem:
    challenge_id: int
    title: str
    bpm: float | None
    duration: float | None
    sheets: list[RhythmSheetSummary]
