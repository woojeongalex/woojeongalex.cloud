from dataclasses import dataclass


@dataclass(frozen=True)
class KaraokeResult:
    """노래방·연주 모드 제출의 서버 채점 결과와 랭킹 위치."""

    score: int
    pitch_accuracy: int
    timing_accuracy: int
    # 로그인하지 않았으면 랭킹에 오르지 않으므로 None
    rank: int | None
    best_score: int | None
    is_personal_best: bool


@dataclass(frozen=True)
class EvaluationResult:
    id: int
    submission_id: int
    score: int
    feedback: str
    next_challenge_id: int | None
    pitch_score: int | None = None
    rhythm_score: int | None = None
    tempo: float | None = None
    karaoke: KaraokeResult | None = None
