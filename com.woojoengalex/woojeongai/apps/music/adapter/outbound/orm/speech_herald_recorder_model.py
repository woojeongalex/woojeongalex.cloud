"""스피치 녹음 입력 — `speech_recordings`."""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlmodel import Field, SQLModel


class SpeechRecordingEntity(SQLModel, table=True):
    __tablename__ = "speech_recordings"

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
    speech_evaluation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("speech_evaluations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )
    topic_id: str = Field(max_length=64, index=True)
    file_name: str = Field(max_length=512, default="")
    duration_sec: int = Field(ge=0, default=0)
    recorded_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
