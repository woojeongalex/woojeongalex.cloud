from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.orm.vocal_bard_searcher_model import SongMrSearchListEntity
from music.app.dtos.search_dto import BardIntroduceQuery, BardIntroduceResponse, SongMrHitDto, SongMrSearchSaveDto
from music.app.ports.output.vocal_bard_searcher_port import ListPort

logger = logging.getLogger(__name__)


class BardSearcherPgRepository(ListPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: BardIntroduceQuery) -> BardIntroduceResponse:
        logger.info("[MUSIC][bard][5/repository] introduce_myself name=%s", query.name)
        return BardIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def get_by_id(self, mr_id: int) -> SongMrHitDto | None:
        stmt = select(SongMrSearchListEntity).where(SongMrSearchListEntity.id == mr_id)
        entity = (await self._session.execute(stmt)).scalar_one_or_none()
        if entity is None:
            return None
        return _to_hit_dto(entity)

    async def save_search_results(
        self, items: list[SongMrSearchSaveDto]
    ) -> list[SongMrHitDto]:
        if not items:
            return []
        rows = [
            SongMrSearchListEntity(
                search_query=item.search_query,
                catalog_song_id=item.catalog_song_id,
                title=item.title,
                artist=item.artist,
                bpm=item.bpm,
                song_key=item.song_key,
                range_label=item.range_label,
                mr_track_name=item.mr_track_name,
                mr_description=item.mr_description,
            )
            for item in items
        ]
        self._session.add_all(rows)
        await self._session.commit()
        for row in rows:
            await self._session.refresh(row)
        logger.info(
            "[MUSIC][bard][5/repository] Neon commit song_mr_search_lists rows=%s ids=%s",
            len(rows),
            [r.id for r in rows],
        )
        return [_to_hit_dto(r) for r in rows]


def _to_hit_dto(e: SongMrSearchListEntity) -> SongMrHitDto:
    return SongMrHitDto(
        id=e.id,
        catalog_song_id=e.catalog_song_id,
        title=e.title,
        artist=e.artist,
        bpm=e.bpm,
        song_key=e.song_key,
        range_label=e.range_label,
        mr_track_name=e.mr_track_name,
        mr_description=e.mr_description,
    )
