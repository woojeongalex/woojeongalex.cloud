from pydantic import BaseModel, Field

class VisionSchema(BaseModel):

    id: int = Field(1, description="Vision ID")
    name: str = Field("Vision", description="Vision name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Vision",
            }
        }
    }
