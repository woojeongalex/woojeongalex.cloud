"""Evaluation(Mia) 의존성 조립소 — 보컬 평가 업로드."""
from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.pg.vocal_mia_recorder_pg_repository import MiaRecorderPgRepository
from music.adapter.outbound.pg.vocal_bard_searcher_pg_repository import BardSearcherPgRepository
from music.app.ports.input.vocal_mia_recorder_use_case import EvaluationUseCase
from music.app.ports.output.vocal_bard_searcher_port import ListPort
from music.app.ports.output.vocal_mia_maestro_port import EvaluationPort
from music.app.use_cases.vocal_mia_recorder_interactor import MiaRecorderInteractor


def get_evaluation_repository(db: AsyncSession = Depends(get_db)) -> EvaluationPort:
    return MiaRecorderPgRepository(session=db)


def get_evaluation_list_repository(db: AsyncSession = Depends(get_db)) -> ListPort:
    return BardSearcherPgRepository(session=db)


def get_evaluation_use_case(
    repository: EvaluationPort = Depends(get_evaluation_repository),
    list_repository: ListPort = Depends(get_evaluation_list_repository),
) -> EvaluationUseCase:
    return MiaRecorderInteractor(repository=repository, list_repository=list_repository)
