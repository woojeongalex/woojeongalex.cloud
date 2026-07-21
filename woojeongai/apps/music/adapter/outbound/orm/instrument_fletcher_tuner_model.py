"""악기 튜닝 평가 세션 허브 + AI 분석 — `instrument_evaluations`, `instrument_tuning_analyses`."""

from datetime import datetime
from typing import Any, Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, func
from sqlmodel import Field, SQLModel


class InstrumentEvaluationEntity(SQLModel, table=True):
    __tablename__ = "instrument_evaluations"

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


class InstrumentTuningAnalysisEntity(SQLModel, table=True):
    __tablename__ = "instrument_tuning_analyses"

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    instrument_recording_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("instrument_recordings.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )
    analysis_engine: str = Field(max_length=64, default="client_demo")
    tuning_accuracy: int = Field(ge=0, le=100, default=0)
    pitch_deviation_cents: int = Field(default=0)
    summary: str = Field(max_length=2048, default="")
    string_readings: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description="현·건반별 편차 요약 JSON",
    )
    analyzed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
