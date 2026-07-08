"""보컬 평가 세션 허브 + AI 분석 — `sing_evaluations`, `ai_vocal_analyses`."""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlmodel import Field, SQLModel


class SingEvaluationEntity(SQLModel, table=True):
    """보컬 평가 세션(허브) 1건. 녹음·MR·카탈로그·점수 정본은 child 테이블에만 둠 (3NF)."""

    __tablename__ = "sing_evaluations"

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
        description="세션 소유자 (평가 대상 아님)",
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )


class AiVocalAnalysisEntity(SQLModel, table=True):
    """사용자 녹음·영상 1건에 대한 AI 평가 결과 (`user_vocal_recordings` 1:1)."""

    __tablename__ = "ai_vocal_analyses"

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_vocal_recording_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("user_vocal_recordings.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )
    analysis_engine: str = Field(
        max_length=32,
        description="예: librosa, mic_demo, client",
    )
    pitch_score: int
    rhythm_score: int
    vocal_grade: str = Field(max_length=32)
    summary: str = Field(max_length=2048)
    analyzed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
