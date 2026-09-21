from dataclasses import dataclass


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
