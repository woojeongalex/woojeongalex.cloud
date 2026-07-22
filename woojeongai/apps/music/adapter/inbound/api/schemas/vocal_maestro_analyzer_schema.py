"""[Layer: Adapter Inbound] Maestro 스키마 — 자기소개 + 보컬 분석."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MaestroIntroduceSchema(BaseModel):
    id: int = Field(0, description="Maestro ID")
    name: str = Field("보컬 마에스트로", description="Maestro's name")


class MaestroIntroduceResponse(BaseModel):
    id: int
    name: str


class VocalEvaluationResponse(BaseModel):
    id: int = Field(description="sing_evaluations.id")
    ok: bool = True
    message: str = "저장되었습니다."


SingEvaluationResponse = VocalEvaluationResponse


class MaestroAnalyzeResponse(BaseModel):
    analysis_id: int = Field(description="ai_vocal_analyses.id")
    pitch_score: int = Field(ge=0, le=100, description="음정 안정성 점수")
    rhythm_score: int = Field(ge=0, le=100, description="리듬 일관성 점수")
    vocal_grade: str = Field(description="종합 등급 (S/A+/A/A-/B+/B/B-/C+/C/D)")
    summary: str = Field(description="AI 분석 요약")
    mean_hz: float = Field(description="평균 기본 음정 (Hz)")
    std_hz: float = Field(description="음정 표준편차 (Hz)")
    tempo: float = Field(description="추정 템포 (BPM)")
    duration: float = Field(description="오디오 길이 (초)")
