"""music_challenge 도메인 ORM.

SQLModel 기반이므로 SQLAlchemy 2.0 의 `Mapped[...]` / `mapped_column()` 을 쓰면
안 된다. SQLModel 은 어노테이션으로 Pydantic 모델을 함께 만들기 때문에
`Mapped[int]` 를 만나면 PydanticSchemaGenerationError 로 임포트 자체가 깨진다.
저장소 표준은 apps/friday13th/.../user_model.py 와 같은 `Field(...)` 스타일이다.

스키마는 alembic/versions/20260824_0008_music_challenge_tables.py 와 일치한다.
"""

from datetime import datetime

from sqlalchemy import Column, Text
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
