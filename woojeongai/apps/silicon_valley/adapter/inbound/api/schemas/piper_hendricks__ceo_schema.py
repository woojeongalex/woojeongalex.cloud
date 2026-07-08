from pydantic import BaseModel, Field


class HendricksCeoSchema(BaseModel):

    id: int = Field(0, description="CEO ID")
    name: str = Field("리처드 헨드릭스", description="CEO's name")
    # 파이드 파이퍼의 CEO. 천재 개발자로 중간값 압축 알고리즘을 개발했지만 사회성은 부족

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5,
                "name": "Richard Hendricks",
            }
        }
    }
