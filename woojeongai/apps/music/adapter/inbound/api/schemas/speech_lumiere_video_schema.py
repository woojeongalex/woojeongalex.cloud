from typing import Any

from pydantic import BaseModel, Field


class LumiereIntroduceSchema(BaseModel):
    id: int = Field(0, description="Lumiere ID")
    name: str = Field("스피치 루미에르", description="Lumiere's name")


class LumiereIntroduceResponse(BaseModel):
    id: int
    name: str


class VideoVocalAnalysisResponse(BaseModel):
    pitch_data: dict[str, Any]
    bpm: float
    duration: float
    emotions: dict[str, float] = Field(default_factory=dict)
