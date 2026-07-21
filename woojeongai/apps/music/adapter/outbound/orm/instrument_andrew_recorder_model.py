"""악기 연주 입력 — `instrument_recordings`."""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlmodel import Field, SQLModel


class InstrumentRecordingEntity(SQLModel, table=True):
    __tablename__ = "instrument_recordings"

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
    instrument_evaluation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("instrument_evaluations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )
    instrument_id: str = Field(max_length=32, description="guitar | piano")
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
