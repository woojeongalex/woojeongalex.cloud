from pydantic import BaseModel, Field


class HendricksChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="리처드에게 보낼 메시지")


class HendricksChatResponse(BaseModel):
    reply: str
