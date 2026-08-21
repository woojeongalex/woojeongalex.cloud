from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    id: int
    submission_id: int
    score: int
    feedback: str
    next_challenge_id: int | None
