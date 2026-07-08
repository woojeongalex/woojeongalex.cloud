"""Maestro 의존성 조립소 — 보컬 마에스트로 자기소개."""
from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.pg.vocal_maestro_analyzer_pg_repository import MaestroAnalyzerPgRepository
from music.app.ports.input.vocal_maestro_analyzer_use_case import MaestroAnalyzerUseCase
from music.app.ports.output.vocal_maestro_analyzer_port import MaestroPort
from music.app.use_cases.vocal_maestro_analyzer_interactor import MaestroAnalyzerInteractor


def get_maestro_repository(db: AsyncSession = Depends(get_db)) -> MaestroPort:
    return MaestroAnalyzerPgRepository(session=db)


def get_maestro_use_case(
    repository: MaestroPort = Depends(get_maestro_repository),
) -> MaestroAnalyzerUseCase:
    return MaestroAnalyzerInteractor(repository=repository)
