from pydantic import BaseModel, Field


class SiliconValleyRequest(BaseModel):
    id: int = Field(0, description="Request ID")
    name: str = Field("", description="Character name")
