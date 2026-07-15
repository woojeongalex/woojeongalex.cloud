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
        """RAG로 답한다: 질문을 임베딩해 관련 곡을 검색하고, 그 컨텍스트를
        참고해 페르소나로 답한다. 임베딩 엔드포인트와 생성 엔드포인트는
        서로 다른 vLLM 인스턴스로 항상 함께 떠 있는 것을 전제로 한다.

        (임시) ship의 8GB GPU 한 장으로는 EXAONE 채팅·임베딩 인스턴스를
        동시에 띄울 수 없어, LOCAL_LLM_EMBED_BASE_URL은 현재 EXAONE이 아닌
        임시 소형 다국어 임베딩 서버(~/small_embed_server.py, port 8003)를
        가리킨다. 브라우저 실시간 채팅의 100초 타임아웃 제약상 요청마다
        vLLM을 채팅↔임베딩으로 전환할 수 없어 이렇게 우회했다 — GPU가
        여유로운 배포 환경에서는 이 대체물 없이 정식 EXAONE 임베딩 인스턴스로
        교체해야 한다."""
        client = get_local_llm_client()

        query_vector = await asyncio.to_thread(client.embed, message)
        songs = await self.song_rag.search_similar_songs(query_vector, limit=5)
        context = _format_song_context(songs)

        system_prompt = (
            f"{HENDRICKS_CEO_SYSTEM_PROMPT}\n\n{context}"
            if context
            else HENDRICKS_CEO_SYSTEM_PROMPT
        )
        return await asyncio.to_thread(client.generate, message, system_prompt)
