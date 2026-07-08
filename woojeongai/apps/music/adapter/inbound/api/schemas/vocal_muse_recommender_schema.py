from pydantic import BaseModel, ConfigDict, Field


class VocalRecommendationCreateRequest(BaseModel):
    sing_evaluation_id: int = Field(ge=1, alias="singEvaluationId")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "singEvaluationId": 1,
            }
        },
    )


class VocalRecommendationResponse(BaseModel):
    id: int = Field(description="vocal_recommendations.id")
    sing_evaluation_id: int = Field(alias="singEvaluationId")
    pitch_score_snapshot: int = Field(
        alias="pitchScoreSnapshot",
        description="DB 비저장 · ai_vocal_analyses 조인값",
    )
    rhythm_score_snapshot: int = Field(
        alias="rhythmScoreSnapshot",
        description="DB 비저장 · ai_vocal_analyses 조인값",
    )
    vocal_grade_snapshot: str = Field(
        alias="vocalGradeSnapshot",
        description="DB 비저장 · ai_vocal_analyses 조인값",
    )
    vocalization_pattern: str = Field(alias="vocalizationPattern")
    recommended_genres: list[str] = Field(alias="recommendedGenres")
    recommended_songs: list[str] = Field(alias="recommendedSongs")

    model_config = ConfigDict(populate_by_name=True)


class MuseIntroduceSchema(BaseModel):
    id: int = Field(0, description="Muse ID")
    name: str = Field("보컬 뮤즈", description="Muse's name")


class MuseIntroduceResponse(BaseModel):
    id: int
    name: str
