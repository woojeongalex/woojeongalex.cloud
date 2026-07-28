from __future__ import annotations

from star_craft.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from star_craft.app.ports.output.langchain_chat_port import LangchainChatPort


class LangchainChatInteractor(LangchainChatUseCase):
    def __init__(self, repository: LangchainChatPort):
        self.repository = repository

    async def chat(self, message: str) -> str:
        return await self.repository.generate(message)
