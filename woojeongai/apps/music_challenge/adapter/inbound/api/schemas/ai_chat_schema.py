from pydantic import BaseModel, Field


class AiChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="사용자 메시지")


class AiChatResponse(BaseModel):
    reply: str
