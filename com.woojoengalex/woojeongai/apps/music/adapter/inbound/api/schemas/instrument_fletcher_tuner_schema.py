from pydantic import BaseModel, Field


class InstrumentEvaluationResponse(BaseModel):
    id: int = Field(description="instrument_evaluations.id")
    ok: bool = True
    message: str = "저장되었습니다."


class FletcherIntroduceSchema(BaseModel):
    id: int = Field(0, description="Fletcher ID")
    name: str = Field("악기 플레처", description="Fletcher's name")


class FletcherIntroduceResponse(BaseModel):
    id: int
    name: str
