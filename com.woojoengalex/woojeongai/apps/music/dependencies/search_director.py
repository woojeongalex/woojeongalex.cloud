"""Search(Bard) 의존성 조립소 — MR 검색·조회."""
from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.pg.vocal_bard_searcher_pg_repository import BardSearcherPgRepository
from music.app.ports.input.vocal_bard_searcher_use_case import SearchUseCase
from music.app.ports.output.vocal_bard_searcher_port import ListPort
from music.app.use_cases.vocal_bard_searcher_interactor import BardSearcherInteractor


def get_search_repository(db: AsyncSession = Depends(get_db)) -> ListPort:
    return BardSearcherPgRepository(session=db)


def get_search_use_case(
    repository: ListPort = Depends(get_search_repository),
) -> SearchUseCase:
    return BardSearcherInteractor(repository=repository)
