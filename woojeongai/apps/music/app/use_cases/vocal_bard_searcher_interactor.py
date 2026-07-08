from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.vocal_bard_searcher_schema import BardIntroduceSchema, BardIntroduceResponse
from music.domain.vocal_bard_searcher_catalog import find_vocal_catalog_by_query
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
        '''Bard의 MR 카탈로그 검색·저장'''
        q = raw_query.strip()
        matches = find_vocal_catalog_by_query(q)
        save_items = [
            SongMrSearchSaveDto(
                search_query=q,
                catalog_song_id=item.id,
                title=item.title,
                artist=item.artist,
                bpm=item.bpm,
                song_key=item.key,
                range_label=item.range_label,
                mr_track_name=item.mr_track_name,
                mr_description=item.mr_description,
            )
            for item in matches
        ]
        if not save_items:
            logger.info(
                "[MUSIC][bard][4/interactor] MR search query=%s match_count=0 (DB 저장 없음)",
                q,
            )
            return SongMrSearchResultDto(query=q, hits=[], count=0)
        hits: list[SongMrHitDto] = await self.repository.save_search_results(save_items)
        logger.info(
            "[MUSIC][bard][4/interactor] MR search query=%s persisted_rows=%s titles=%s",
            q,
            len(hits),
            [h.title for h in hits],
        )
        return SongMrSearchResultDto(query=q, hits=hits, count=len(hits))
