from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.vocal_bard_searcher_schema import BardIntroduceSchema, BardIntroduceResponse
from music.app.dtos.search_dto import BardIntroduceQuery, SongMrHitDto, SongMrSearchResultDto, SongMrSearchSaveDto
from music.app.ports.input.vocal_bard_searcher_use_case import SearchUseCase
from music.app.ports.output.vocal_bard_searcher_port import ListPort

logger = logging.getLogger(__name__)


class BardSearcherInteractor(SearchUseCase):
    def __init__(self, repository: ListPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: BardIntroduceSchema) -> BardIntroduceResponse:
        return await self.repository.introduce_myself(BardIntroduceQuery(id=schema.id, name=schema.name))

    async def search(self, raw_query: str) -> SongMrSearchResultDto:
        q = raw_query.strip()

        catalog_hits: list[SongMrHitDto] = await self.repository.search_catalog(q)

        if not catalog_hits:
            logger.info("[MUSIC][bard][4/interactor] query=%s results=0", q)
            return SongMrSearchResultDto(query=q, hits=[], count=0)

        save_items = [
            SongMrSearchSaveDto(
                search_query=q,
                catalog_song_id=hit.catalog_song_id,
                title=hit.title,
                artist=hit.artist,
                bpm=hit.bpm,
                song_key=hit.song_key,
                range_label=hit.range_label,
                mr_track_name=hit.mr_track_name,
                mr_description=hit.mr_description,
            )
            for hit in catalog_hits
        ]

        persisted: list[SongMrHitDto] = await self.repository.save_search_results(save_items)

        logger.info("[MUSIC][bard][4/interactor] query=%s persisted=%s", q, len(persisted))
        return SongMrSearchResultDto(query=q, hits=persisted, count=len(persisted))
