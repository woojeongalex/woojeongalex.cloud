from __future__ import annotations

import asyncio

from music_challenge.app.ports.input.ai_chat_use_case import AiChatUseCase
from music_challenge.app.ports.output.ai_chat_port import AiChatPort


class AiChatInteractor(AiChatUseCase):
    def __init__(self, chat: AiChatPort):
        self._chat = chat

    async def chat(self, message: str) -> str:
        # 어댑터가 동기 SDK 를 쓰므로 이벤트 루프를 막지 않도록 스레드로 넘긴다.
        return await asyncio.to_thread(self._chat.generate, message)
