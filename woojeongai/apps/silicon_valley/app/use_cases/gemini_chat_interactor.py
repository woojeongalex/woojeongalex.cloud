from __future__ import annotations

import asyncio

from silicon_valley.app.ports.input.gemini_chat_use_case import GeminiChatUseCase
from silicon_valley.app.ports.output.gemini_port import GeminiPort


class GeminiChatInteractor(GeminiChatUseCase):
    def __init__(self, gemini: GeminiPort):
        self.gemini = gemini

    async def chat(self, message: str) -> str:
        return await asyncio.to_thread(self.gemini.generate, message)
