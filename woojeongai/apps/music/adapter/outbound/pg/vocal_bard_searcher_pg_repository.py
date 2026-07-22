from __future__ import annotations

import logging

from sqlalchemy import select, or_, Table, Column, String, Integer, MetaData
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.orm.vocal_bard_searcher_model import SongMrSearchListEntity
from music.app.dtos.search_dto import BardIntroduceQuery, BardIntroduceResponse, SongMrHitDto, SongMrSearchSaveDto
from music.app.ports.output.vocal_bard_searcher_port import ListPort

logger = logging.getLogger(__name__)

_catalog_songs = Table(
    "catalog_songs",
    MetaData(),
    Column("catalog_song_id", String(64), primary_key=True),
    Column("title", String(256)),
    Column("artist", String(256)),
    Column("bpm", Integer),
    Column("song_key", String(64)),
    Column("range_label", String(128)),
    Column("mr_track_name", String(256)),
    Column("mr_description", String(512)),
)


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
        return _to_hit_dto_from_mr(entity)

    async def search_catalog(self, query: str) -> list[SongMrHitDto]:
        needle = f"%{query}%"
        stmt = (
            select(_catalog_songs)
            .where(
                or_(
                    _catalog_songs.c.title.ilike(needle),
                    _catalog_songs.c.artist.ilike(needle),
                    _catalog_songs.c.mr_track_name.ilike(needle),
                    _catalog_songs.c.mr_description.ilike(needle),
                    _catalog_songs.c.range_label.ilike(needle),
                )
            )
            .limit(20)
        )
        rows = (await self._session.execute(stmt)).mappings().all()
        logger.info("[MUSIC][bard][5/repository] catalog search query=%s hits=%s", query, len(rows))
        return [
            SongMrHitDto(
                id=0,
                catalog_song_id=r["catalog_song_id"],
                title=r["title"],
                artist=r["artist"],
                bpm=r["bpm"],
                song_key=r["song_key"],
                range_label=r["range_label"],
                mr_track_name=r["mr_track_name"],
                mr_description=r["mr_description"],
            )
            for r in rows
        ]

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
            "[MUSIC][bard][5/repository] commit song_mr_search_lists rows=%s ids=%s",
            len(rows),
            [r.id for r in rows],
        )
        return [_to_hit_dto_from_mr(r) for r in rows]


def _to_hit_dto_from_mr(e: SongMrSearchListEntity) -> SongMrHitDto:
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
