from pydantic import BaseModel


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
