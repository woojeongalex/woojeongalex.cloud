"""Suggest(Muse) 의존성 조립소 — 추천 업로드·조회."""
from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.pg.vocal_muse_recommender_pg_repository import MuseRecommenderPgRepository
from music.app.ports.input.vocal_muse_recommender_use_case import SuggestUseCase
from music.app.ports.output.vocal_muse_recommender_port import SuggestPort
from music.app.use_cases.vocal_muse_recommender_interactor import MuseRecommenderInteractor


def get_suggest_repository(db: AsyncSession = Depends(get_db)) -> SuggestPort:
    return MuseRecommenderPgRepository(session=db)


def get_suggest_use_case(
    repository: SuggestPort = Depends(get_suggest_repository),
) -> SuggestUseCase:
    return MuseRecommenderInteractor(repository=repository)
