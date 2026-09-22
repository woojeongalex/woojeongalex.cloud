from dataclasses import dataclass
from datetime import datetime

from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.value_objects.rhythm_vo import RhythmDifficulty, RhythmSheet


@dataclass(frozen=True)
class RhythmChart:
    """곡 하나의 리듬 게임 채보 묶음(4키·7키 × 쉬움·보통·어려움).

    job_id 는 지금 진행 중인(또는 마지막으로 끝난) 생성 작업이다. 생성 중에 다시
    요청하면 새 job_id 가 들어가고, 늦게 끝난 옛 작업은 결과를 버린다.
    """

    challenge_id: int
    status: ChartStatus
    job_id: str | None
    bpm: float | None
    duration: float | None
    sheets: list[RhythmSheet]
    error: str | None
    updated_at: datetime

    def sheet(self, keys: int, difficulty: RhythmDifficulty) -> RhythmSheet | None:
        return next(
            (s for s in self.sheets if s.keys == keys and s.difficulty == difficulty),
            None,
        )


@dataclass(frozen=True)
class RhythmPlay:
    """한 판의 결과. 점수는 서버가 입력 기록으로 다시 계산한 값이다."""

    id: int
    challenge_id: int
    user_id: int | None
    keys: int
    difficulty: RhythmDifficulty
    score: int
    accuracy: float
    max_combo: int
    cool: int
    good: int
    bad: int
    miss: int
    created_at: datetime
