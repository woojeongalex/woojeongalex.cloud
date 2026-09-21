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
    # librosa 로 측정한 객관 지표. 분석 불가(영상 등)면 None.
    pitch_score: int | None = None
    rhythm_score: int | None = None
    tempo: float | None = None
