from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SubmissionHistoryItem:
    """내 도전 기록 한 줄 — 제출 + 챌린지 + 평가를 합친 읽기 전용 모델.

    평가가 아직 없거나(이론상) 실패한 제출도 기록에는 남아야 하므로
    점수 계열은 전부 optional 이다.
    """

    submission_id: int
    challenge_id: int
    challenge_title: str
    challenge_type: str
    media_type: str
    created_at: datetime
    score: int | None = None
    pitch_score: int | None = None
    rhythm_score: int | None = None
