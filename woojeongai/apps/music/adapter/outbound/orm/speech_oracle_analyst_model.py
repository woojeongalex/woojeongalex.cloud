"""스피치 코칭 세션 허브 + AI 피드백 — `speech_evaluations`, `speech_feedback_analyses`."""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, func
from sqlmodel import Field, SQLModel


class SpeechEvaluationEntity(SQLModel, table=True):
    __tablename__ = "speech_evaluations"

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )


class SpeechFeedbackAnalysisEntity(SQLModel, table=True):
    __tablename__ = "speech_feedback_analyses"

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    speech_recording_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("speech_recordings.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )
    analysis_engine: str = Field(max_length=64, default="client_demo")
    clarity_score: int = Field(ge=0, le=100, default=0)
    pace_score: int = Field(ge=0, le=100, default=0)
    tone_score: int = Field(ge=0, le=100, default=0)
    summary: str = Field(max_length=2048, default="")
    feedback_points: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    analyzed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
