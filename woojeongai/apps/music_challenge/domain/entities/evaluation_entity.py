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
    # 노래방·연주 모드로 제출했을 때만. 정답 음표 대비 서버 재채점 결과.
    karaoke_score: int | None = None
    karaoke_pitch_accuracy: int | None = None
    karaoke_timing_accuracy: int | None = None
