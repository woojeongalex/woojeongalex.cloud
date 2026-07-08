from pydantic import BaseModel, Field


class SiliconValleySchema(BaseModel):
    id: int = Field(0, description="ID")
    name: str = Field("", description="Name")
