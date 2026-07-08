from pydantic import BaseModel, Field


class SpeechEvaluationResponse(BaseModel):
    id: int = Field(description="speech_evaluations.id")
    ok: bool = True
    message: str = "저장되었습니다."


class OracleIntroduceSchema(BaseModel):
    id: int = Field(0, description="Oracle ID")
    name: str = Field("스피치 오라클", description="Oracle's name")


class OracleIntroduceResponse(BaseModel):
    id: int
    name: str
