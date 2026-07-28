from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from core.matrix.keymaker_api import Keymaker
from star_craft.app.ports.output.langchain_chat_port import LangchainChatPort
from star_craft.domain.constants.langchain_chat_persona import (
    LANGCHAIN_CODING_SYSTEM_PROMPT,
)

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", LANGCHAIN_CODING_SYSTEM_PROMPT),
        ("human", "{message}"),
    ]
)


class LangchainChatRepository(LangchainChatPort):
    """LangChain 체인(ChatPromptTemplate | ChatGoogleGenerativeAI)으로 Gemini를 호출한다."""

    def __init__(self, keymaker: Keymaker) -> None:
        if not keymaker.is_gemini_ready():
            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았습니다. backend/.env를 확인하세요."
            )
        llm = ChatGoogleGenerativeAI(
            model=keymaker.get_gemini_model_name(),
            google_api_key=keymaker.get_gemini_api_key(),
        )
        self._chain = _PROMPT | llm

    async def generate(self, message: str) -> str:
        result = await self._chain.ainvoke({"message": message})
        return str(result.content).strip()
