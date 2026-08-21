from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SubmissionEvaluation:
    id: int
    submission_id: int
    score: int
    feedback: str
    next_challenge_id: int | None
    created_at: datetime
