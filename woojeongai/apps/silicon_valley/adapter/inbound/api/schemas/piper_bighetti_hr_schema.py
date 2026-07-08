from pydantic import BaseModel, Field


class BighettiHrSchema(BaseModel):

    id: int = Field(0, description="Employee ID")
    name: str = Field("넬슨 비게티", description="Employee's name")
    # 파이드 파이퍼의 HR 담당. 리처드의 절친이자 운이 좋아 Hooli에서 승승장구한 인물

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Nelson Bighetti",
            }
        }
    }
