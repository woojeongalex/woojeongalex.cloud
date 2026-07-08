from pydantic import BaseModel, Field


class DineshDashSchema(BaseModel):

    id: int = Field(0, description="Developer ID")
    name: str = Field("디네시 추크타이", description="Developer's name")
    # 파이드 파이퍼의 백엔드 개발자. 대시보드 담당으로 자존심 강하고 길포일과 라이벌 관계

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "name": "Dinesh Chugtai",
            }
        }
    }
