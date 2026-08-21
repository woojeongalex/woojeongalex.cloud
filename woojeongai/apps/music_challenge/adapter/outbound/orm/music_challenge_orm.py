from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlmodel import SQLModel


class MusicChallengeModel(SQLModel, table=True):
    __tablename__ = "music_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    music_s3_key: Mapped[str] = mapped_column(String(500))
    challenge_type: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class ChallengeSubmissionModel(SQLModel, table=True):
    __tablename__ = "challenge_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[int] = mapped_column(Integer, ForeignKey("music_challenges.id"))
    media_type: Mapped[str] = mapped_column(String(10))
    s3_key: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class SubmissionEvaluationModel(SQLModel, table=True):
    __tablename__ = "submission_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("challenge_submissions.id"))
    score: Mapped[int] = mapped_column(Integer)
    feedback: Mapped[str] = mapped_column(Text)
    next_challenge_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("music_challenges.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
