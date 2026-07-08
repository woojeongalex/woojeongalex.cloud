from pydantic import BaseModel, Field


class DunnCooSchema(BaseModel):

    id: int = Field(0, description="COO ID")
    name: str = Field("자레드 던", description="COO's name")
    # 파이드 파이퍼의 COO. 전 Hooli 직원으로 충성심이 강하고 뛰어난 비즈니스 감각을 가진 인물

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "name": "Jared Dunn",
            }
        }
    }
