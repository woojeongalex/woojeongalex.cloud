"""보컬 평가 기반 장르·곡 추천 — `vocal_recommendations`."""

from datetime import datetime
from typing import Any, Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, func
from sqlmodel import Field, SQLModel


class VocalRecommendationEntity(SQLModel, table=True):
    """평가 세션 1건에 대한 추천. 표시용 점수는 `ai_vocal_analyses`에서 조인."""

    __tablename__ = "vocal_recommendations"

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, primary_key=True)

    sing_evaluation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sing_evaluations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        description="FK → sing_evaluations.id",
    )
    ai_vocal_analysis_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("ai_vocal_analyses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        description="FK → 분석 결과 (추천 생성 시점의 정본 참조)",
    )

    vocalization_pattern: str = Field(
        max_length=1024,
        description="음정·박자·발성 기준 요약(배너 설명문)",
    )

    recommended_genres: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description='예: ["발라드", "뮤지컬 넘버"]',
    )
    recommended_songs: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description='예: ["밤편지", "Defying Gravity"]',
    )

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
