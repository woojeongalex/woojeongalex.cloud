from fastapi import APIRouter, Depends, Query

from music.adapter.inbound.api.mappers.music_inbound_mapper import to_search_response
from music.adapter.inbound.api.schemas.vocal_bard_searcher_schema import BardIntroduceSchema, BardIntroduceResponse, SongMrSearchResponse
from music.app.ports.input.vocal_bard_searcher_use_case import SearchUseCase
from music.adapter.inbound.api.deps.music_deps import get_search_use_case

vocal_bard_searcher_router = APIRouter(tags=["music-search"])


@vocal_bard_searcher_router.get("/api/music/bard/myself", response_model=BardIntroduceResponse)
async def bard_introduce_myself(
    bard: SearchUseCase = Depends(get_search_use_case),
) -> BardIntroduceResponse:
    return await bard.introduce_myself(BardIntroduceSchema(id=1, name="보컬 바드 (Vocal Bard)"))


@vocal_bard_searcher_router.get("/api/songs/search", response_model=SongMrSearchResponse)
async def songs_search(
    q: str = Query(..., min_length=1, description="노래 제목·MR·아티스트 검색어"),
    search: SearchUseCase = Depends(get_search_use_case),
) -> SongMrSearchResponse:
    return to_search_response(await search.search(q))
