"""Oracle 의존성 조립소 — 스피치 오라클 자기소개."""
from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.pg.speech_oracle_analyst_pg_repository import OracleAnalystPgRepository
from music.app.ports.input.speech_oracle_analyst_use_case import OracleAnalystUseCase
from music.app.ports.output.speech_oracle_analyst_port import OraclePort
from music.app.use_cases.speech_oracle_analyst_interactor import OracleAnalystInteractor


def get_oracle_repository(db: AsyncSession = Depends(get_db)) -> OraclePort:
    return OracleAnalystPgRepository(session=db)


def get_oracle_use_case(
    repository: OraclePort = Depends(get_oracle_repository),
) -> OracleAnalystUseCase:
    return OracleAnalystInteractor(repository=repository)
