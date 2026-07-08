"""Fletcher 의존성 조립소 — 악기 플레처 자기소개."""
from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.pg.instrument_fletcher_tuner_pg_repository import FletcherTunerPgRepository
from music.app.ports.input.instrument_fletcher_tuner_use_case import FletcherTunerUseCase
from music.app.ports.output.instrument_fletcher_tuner_port import FletcherPort
from music.app.use_cases.instrument_fletcher_tuner_interactor import FletcherTunerInteractor


def get_fletcher_repository(db: AsyncSession = Depends(get_db)) -> FletcherPort:
    return FletcherTunerPgRepository(session=db)


def get_fletcher_use_case(
    repository: FletcherPort = Depends(get_fletcher_repository),
) -> FletcherTunerUseCase:
    return FletcherTunerInteractor(repository=repository)
