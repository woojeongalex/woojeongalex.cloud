from pydantic import BaseModel, Field


class GeminiChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="사용자 메시지")


class GeminiChatResponse(BaseModel):
    reply: str
