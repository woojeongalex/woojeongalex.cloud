from typing import Literal

from pydantic import BaseModel, Field



class ChatSchema(BaseModel):
    messages: str = Field(..., description="사용자가 채팅창에 입력한 자연어")

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": "탑승객이 몇 명이야?",
            }
        }
    }



class SmithCaptainSchema(BaseModel):
    id: int = Field(0, description="Captain ID")
    name: str = Field("에드워드 존 스미스", description="Captain's name")
    model_type: Literal["jack", "rose"] = Field("jack", description="사용할 모델 선택 (jack 또는 rose)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "name": "Edward John Smith",
                "model_type": "jack",
            }
        }
    }



