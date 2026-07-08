from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AndrewIntroduceSchema(BaseModel):
    id: int = Field(0, description="Andrew ID")
    name: str = Field("악기 앤드류", description="Andrew's name")


class AndrewIntroduceResponse(BaseModel):
    id: int
    name: str


class InstrumentEvaluationCreateRequest(BaseModel):
    instrument_id: Literal["guitar", "piano"] = Field(alias="instrumentId")
    tuning_accuracy: int = Field(ge=0, le=100, alias="tuningAccuracy")
    pitch_deviation_cents: int = Field(alias="pitchDeviationCents")
    summary: str = Field(max_length=2048)
    string_readings: list[dict[str, Any]] = Field(
        default_factory=list, alias="stringReadings"
    )
    file_name: str = Field(default="", max_length=512, alias="fileName")
    duration_sec: int = Field(default=0, ge=0, alias="durationSec")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "instrumentId": "guitar",
                "tuningAccuracy": 88,
                "pitchDeviationCents": -5,
                "summary": "E 현 튜닝이 약간 낮습니다.",
                "stringReadings": [{"string": "E", "cents": -5}, {"string": "A", "cents": 0}],
                "fileName": "guitar_session.mp3",
                "durationSec": 120,
            }
        },
    )
