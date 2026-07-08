from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.repositories.crew_james_repository import JamesRepository
from titanic.app.ports.input.crew_james_use_case import JamesUseCase
from titanic.app.ports.output.crew_james_port import JamesPort
from titanic.app.use_cases.crew_james_director_interactor import JamesDirectorInteractor


def get_james_repository(db: AsyncSession = Depends(get_db)) -> JamesPort:
    return JamesRepository(session=db)


def get_james_use_case(
    repository: JamesPort = Depends(get_james_repository)
) -> JamesUseCase:
    return JamesDirectorInteractor(repository=repository)
