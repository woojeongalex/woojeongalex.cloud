from pydantic import BaseModel, Field


class GilfoyleSystemSchema(BaseModel):

    id: int = Field(0, description="System Architect ID")
    name: str = Field("버트람 길포일", description="System Architect's name")
    # 파이드 파이퍼의 시스템 아키텍트. 냉소적이고 능력 있으며 서버 인프라 전반을 담당

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "name": "Bertram Gilfoyle",
            }
        }
    }
