"""music_challenge 도메인 ORM.

SQLModel 기반이므로 SQLAlchemy 2.0 의 `Mapped[...]` / `mapped_column()` 을 쓰면
안 된다. SQLModel 은 어노테이션으로 Pydantic 모델을 함께 만들기 때문에
`Mapped[int]` 를 만나면 PydanticSchemaGenerationError 로 임포트 자체가 깨진다.
저장소 표준은 apps/friday13th/.../user_model.py 와 같은 `Field(...)` 스타일이다.

스키마는 alembic/versions/20260824_0008_music_challenge_tables.py 와 일치한다.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class MusicChallengeModel(SQLModel, table=True):
    __tablename__ = "music_challenges"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(sa_column=Column(Text, nullable=False))
    music_s3_key: str = Field(max_length=500)
    challenge_type: str = Field(max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChallengeSubmissionModel(SQLModel, table=True):
    __tablename__ = "challenge_submissions"

    id: int | None = Field(default=None, primary_key=True)
    challenge_id: int = Field(foreign_key="music_challenges.id", index=True)
    # 비로그인 참여도 허용하므로 nullable. 값은 반드시 서버가 JWT 에서 도출한다.
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    media_type: str = Field(max_length=10)
    s3_key: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionEvaluationModel(SQLModel, table=True):
    __tablename__ = "submission_evaluations"

    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="challenge_submissions.id", index=True)
    score: int
    feedback: str = Field(sa_column=Column(Text, nullable=False))
    next_challenge_id: int | None = Field(
        default=None, foreign_key="music_challenges.id"
    )
    # librosa 신호 분석 결과. 영상 등 분석 불가 입력이면 비어 있다.
    pitch_score: int | None = Field(default=None)
    rhythm_score: int | None = Field(default=None)
    tempo: float | None = Field(default=None)
    # 노래방·연주 모드 제출만. 정답 음표 대비 서버 재채점 결과이며 랭킹은 이 값만 쓴다.
    karaoke_score: int | None = Field(default=None, index=True)
    karaoke_pitch_accuracy: int | None = Field(default=None)
    karaoke_timing_accuracy: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChallengeChartModel(SQLModel, table=True):
    """노래방·연주 화면용 악보 — 정답 멜로디, 가사 타이밍, 스템 위치.

    목록 조회마다 수백 개의 음표를 실어 나르지 않도록 챌린지와 분리했다.
    melody 는 정답을 뽑는 트랙(보컬 또는 멜로디 악기), backing 은 도전 때 트는 반주다.
    """

    __tablename__ = "challenge_charts"
    challenge_id: int = Field(foreign_key="music_challenges.id", primary_key=True)
    # empty | processing | ready | failed
    status: str = Field(default="empty", max_length=20)
    notes: list | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    duration: float | None = Field(default=None)
    # vocal | instrument
    melody_source: str = Field(default="vocal", max_length=20)
    # piano | guitar | violin | flute | saxophone | other. 보컬이면 비어 있다.
    instrument: str | None = Field(default=None, max_length=20)
    melody_s3_key: str | None = Field(default=None, max_length=500)
    backing_s3_key: str | None = Field(default=None, max_length=500)
    lyric_lines: list | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RhythmChartModel(SQLModel, table=True):
    """리듬 게임 채보 묶음 — 곡 하나에 4키·7키 × 쉬움·보통·어려움.

    sheets 는 [{"keys", "difficulty", "level", "notes": [[time, lane, end|null], ...]}].
    노트가 수천 개라 객체 대신 배열로 줄여 저장한다.
    """

    __tablename__ = "rhythm_charts"
    challenge_id: int = Field(foreign_key="music_challenges.id", primary_key=True)
    # empty | processing | ready | failed
    status: str = Field(default="empty", max_length=20)
    job_id: str | None = Field(default=None, max_length=64)
    bpm: float | None = Field(default=None)
    duration: float | None = Field(default=None)
    sheets: list | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RhythmPlayModel(SQLModel, table=True):
    """리듬 게임 한 판. 점수는 서버가 입력 기록으로 다시 계산한 값이다."""

    __tablename__ = "rhythm_plays"

    id: int | None = Field(default=None, primary_key=True)
    challenge_id: int = Field(foreign_key="music_challenges.id")
    # 비로그인 플레이도 남기지만 랭킹에는 오르지 않는다. 값은 서버가 JWT 에서 도출한다.
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    keys: int
    difficulty: str = Field(max_length=10)
    score: int
    accuracy: float
    max_combo: int
    cool: int
    good: int
    bad: int
    miss: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
