from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.repositories.passenger_ruth_survivor_repository import RuthSurvivorRepository
from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthSurvivorUseCase
from titanic.app.ports.output.passenger_ruth_survivor_port import RuthSurvivorPort
from titanic.app.use_cases.passenger_ruth_survivor_interactor import RuthSurvivorInteractor


def get_ruth_survivor_repository(db: AsyncSession = Depends(get_db)) -> RuthSurvivorPort:
    return RuthSurvivorRepository(session=db)


def get_ruth_survivor_use_case(
    repository: RuthSurvivorPort = Depends(get_ruth_survivor_repository)
) -> RuthSurvivorUseCase:
    return RuthSurvivorInteractor(repository=repository)
