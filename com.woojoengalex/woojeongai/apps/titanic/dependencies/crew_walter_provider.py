from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.repositories.crew_walter_repository import WalterRepository
from titanic.app.ports.input.crew_walter_use_case import WalterUseCase
from titanic.app.ports.output.crew_walter_director_port import WalterDirectorPort
from titanic.app.use_cases.crew_walter_interactor import WalterInteractor


def get_walter_repository(db: AsyncSession = Depends(get_db)) -> WalterDirectorPort:
    return WalterRepository(session=db)


def get_walter_use_case(
    repository: WalterDirectorPort = Depends(get_walter_repository)
) -> WalterUseCase:
    return WalterInteractor(repository=repository)
