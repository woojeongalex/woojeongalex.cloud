from pydantic import BaseModel, Field


class SpeechTopicHit(BaseModel):
    topic_id: str
    label: str
    description: str


class SpeechTopicsResponse(BaseModel):
    hits: list[SpeechTopicHit]
    count: int


class CiceroIntroduceSchema(BaseModel):
    id: int = Field(0, description="Cicero ID")
    name: str = Field("스피치 키케로", description="Cicero's name")


class CiceroIntroduceResponse(BaseModel):
    id: int
    name: str
