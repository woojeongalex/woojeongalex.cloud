from pydantic import BaseModel, Field


class VocalEvaluationResponse(BaseModel):
    id: int = Field(description="sing_evaluations.id")
    ok: bool = True
    message: str = "저장되었습니다."


SingEvaluationResponse = VocalEvaluationResponse


class MaestroIntroduceSchema(BaseModel):
    id: int = Field(0, description="Maestro ID")
    name: str = Field("보컬 마에스트로", description="Maestro's name")


class MaestroIntroduceResponse(BaseModel):
    id: int
    name: str
