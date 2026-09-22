from datetime import datetime

from pydantic import BaseModel


class KaraokeResultResponse(BaseModel):
    score: int
    pitch_accuracy: int
    timing_accuracy: int
    rank: int | None
    best_score: int | None
    is_personal_best: bool


class EvaluationResponse(BaseModel):
    id: int
    submission_id: int
    score: int
    feedback: str
    next_challenge_id: int | None
    # 신호 분석 기반 객관 지표 — 화면에서 종합 점수와 따로 보여준다
    pitch_score: int | None = None
    rhythm_score: int | None = None
    tempo: float | None = None
    # 노래방·연주 모드 제출만 — 정답 음표 대비 서버 채점과 랭킹 위치
    karaoke: KaraokeResultResponse | None = None


class SubmissionHistoryItemResponse(BaseModel):
    submission_id: int
    challenge_id: int
    challenge_title: str
    challenge_type: str
    media_type: str
    created_at: datetime
    score: int | None = None
    pitch_score: int | None = None
    rhythm_score: int | None = None


class SubmissionHistoryResponse(BaseModel):
    items: list[SubmissionHistoryItemResponse]
    total: int
