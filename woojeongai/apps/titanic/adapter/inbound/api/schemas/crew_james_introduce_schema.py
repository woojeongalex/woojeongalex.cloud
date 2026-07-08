from pydantic import BaseModel, Field


class JamesIntroduceSchema(BaseModel):
    id: int = Field(0, description="Director ID")
    name: str = Field("제임스 카메론", description="Director's name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "James Cameron",
            }
        }
    }
