from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VocalEvaluationCreateRequest(BaseModel):
    pitch_score: int = Field(
        ge=0,
        le=100,
        alias="pitchScore",
        description="음정 정확도 (%)",
    )
    rhythm_score: int = Field(
        ge=0,
        le=100,
        alias="rhythmScore",
        description="박자 정확도 (%)",
    )
    vocal_grade: str = Field(
        max_length=32,
        alias="vocalGrade",
        description="AI 피드백 등급 (예: A-)",
    )
    summary: str = Field(max_length=2048, description="AI 피드백 요약")
    catalog_song_id: str | None = Field(
        default=None,
        max_length=64,
        alias="catalogSongId",
        description="선택 곡. mrSearchListId 있으면 MR 행 catalog로 정합 → user_vocal_recordings",
    )
    mr_search_list_id: int | None = Field(
        default=None,
        ge=1,
        alias="mrSearchListId",
        description="녹음에 사용한 song_mr_search_lists.id (uses_mr 정본)",
    )
    input_source: Literal["mic", "video"] = Field(
        alias="inputSource",
        description="mic | video",
    )
    file_name: str = Field(default="", max_length=512, alias="fileName")
    duration_sec: int = Field(default=0, ge=0, alias="durationSec")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "pitchScore": 82,
                "rhythmScore": 75,
                "vocalGrade": "B+",
                "summary": "음정은 안정적이나 고음 구간 박자 이탈이 있습니다.",
                "catalogSongId": "through-the-night",
                "mrSearchListId": 3,
                "inputSource": "mic",
                "fileName": "vocal_take1.mp3",
                "durationSec": 180,
            }
        },
    )


SingEvaluationCreateRequest = VocalEvaluationCreateRequest


class MiaIntroduceSchema(BaseModel):
    id: int = Field(0, description="Mia ID")
    name: str = Field("보컬 미아", description="Mia's name")


class MiaIntroduceResponse(BaseModel):
    id: int
    name: str
