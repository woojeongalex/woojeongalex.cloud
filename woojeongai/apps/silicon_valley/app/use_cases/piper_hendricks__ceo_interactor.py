from __future__ import annotations

import asyncio

from core.matrix.local_llm_client import get_local_llm_client
from silicon_valley.app.dtos.piper_hendricks__ceo_dto import (
    HendricksCeoQuery,
    HendricksCeoResponse,
)
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import (
    HendricksCeoUseCase,
)
from silicon_valley.app.ports.output.piper_hendricks__ceo_port import HendricksCeoPort
from silicon_valley.app.ports.output.song_rag_port import SongRagPort
from silicon_valley.domain.constants.piper_personas import HENDRICKS_CEO_SYSTEM_PROMPT


def _format_song_context(songs: list[dict[str, str | None]]) -> str:
    if not songs:
        return ""
    lines = [
        f"- {song.get('title')} ({song.get('artist')}): {song.get('mr_description') or ''}"
        for song in songs
    ]
    return "참고할 수 있는 곡 정보:\n" + "\n".join(lines)


class HendricksCeoInteractor(HendricksCeoUseCase):
    def __init__(self, repository: HendricksCeoPort, song_rag: SongRagPort):
        self.repository = repository
        self.song_rag = song_rag

    async def introduce_myself(self, request) -> HendricksCeoResponse:
        return await self.repository.introduce_myself(
            HendricksCeoQuery(
                id=request.id,
                name=request.name,
            )
        )

    async def get_company_status(self) -> dict:
        return {}

    async def chat(self, message: str) -> str:
        """RAG로 답한다: 임베딩 모드로 전환해 질문을 벡터화하고 관련 곡을 검색한 뒤,
        채팅 모드로 되돌아와 그 컨텍스트를 참고해 페르소나로 답한다.
        8GB GPU 한 장으로 두 모드를 동시에 못 띄워 매 요청마다 모드 전환이 발생한다."""
        client = get_local_llm_client()

        await asyncio.to_thread(client.switch_to_embed)
        query_vector = await asyncio.to_thread(client.embed, message)

        songs = await self.song_rag.search_similar_songs(query_vector, limit=5)
        context = _format_song_context(songs)

        await asyncio.to_thread(client.switch_to_chat)
        system_prompt = (
            f"{HENDRICKS_CEO_SYSTEM_PROMPT}\n\n{context}"
            if context
            else HENDRICKS_CEO_SYSTEM_PROMPT
        )
        return await asyncio.to_thread(client.generate, message, system_prompt)
