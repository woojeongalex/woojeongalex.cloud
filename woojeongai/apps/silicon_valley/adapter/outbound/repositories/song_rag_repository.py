from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.app.ports.output.song_rag_port import SongRagPort


class SongRagRepository(SongRagPort):
    """RAG 컨텍스트 용도로 music 앱의 catalog_songs를 읽기 전용 조회한다."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_similar_songs(
        self, embedding: list[float], limit: int = 5
    ) -> list[dict[str, str | None]]:
        result = await self.session.execute(
            text(
                "SELECT title, artist, mr_description"
                " FROM catalog_songs"
                " WHERE embedding IS NOT NULL"
                " ORDER BY embedding <=> :query_vector"
                " LIMIT :limit"
            ),
            {"query_vector": str(embedding), "limit": limit},
        )
        return [dict(row._mapping) for row in result.fetchall()]
