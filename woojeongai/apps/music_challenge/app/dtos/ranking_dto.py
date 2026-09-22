from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RankingEntry:
    rank: int
    nickname: str
    score: int
    pitch_accuracy: int | None
    timing_accuracy: int | None
    achieved_at: datetime


@dataclass(frozen=True)
class WeeklyRankingEntry(RankingEntry):
    challenge_id: int
    challenge_title: str


@dataclass(frozen=True)
class MyStanding:
    """한 곡에서 내 최고 기록과 그 순위."""

    rank: int
    best_score: int
