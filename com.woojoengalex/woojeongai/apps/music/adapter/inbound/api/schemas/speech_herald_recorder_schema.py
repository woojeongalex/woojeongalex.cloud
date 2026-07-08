from pydantic import BaseModel, ConfigDict, Field


class HeraldIntroduceSchema(BaseModel):
    id: int = Field(0, description="Herald ID")
    name: str = Field("스피치 헤럴드", description="Herald's name")


class HeraldIntroduceResponse(BaseModel):
    id: int
    name: str


class SpeechEvaluationCreateRequest(BaseModel):
    topic_id: str = Field(max_length=64, alias="topicId")
    clarity_score: int = Field(ge=0, le=100, alias="clarityScore")
    pace_score: int = Field(ge=0, le=100, alias="paceScore")
    tone_score: int = Field(ge=0, le=100, alias="toneScore")
    summary: str = Field(max_length=2048)
    feedback_points: list[str] = Field(default_factory=list, alias="feedbackPoints")
    file_name: str = Field(default="", max_length=512, alias="fileName")
    duration_sec: int = Field(default=0, ge=0, alias="durationSec")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "topicId": "presentation",
                "clarityScore": 78,
                "paceScore": 82,
                "toneScore": 70,
                "summary": "발음은 명확하나 발표 속도가 약간 빠릅니다.",
                "feedbackPoints": ["속도 조절 필요", "어미 처리 개선"],
                "fileName": "speech_practice.mp3",
                "durationSec": 90,
            }
        },
    )
