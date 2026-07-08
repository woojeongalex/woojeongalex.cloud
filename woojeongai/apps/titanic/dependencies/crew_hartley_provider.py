from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.repositories.crew_hartley_violin_repository import HartleyViolinRepository
from titanic.app.ports.input.crew_hartley_use_case import HartleyUseCase
from titanic.app.ports.output.crew_hartley_violin_port import HartleyViolinPort
from titanic.app.use_cases.crew_hartley_violin_interactor import HartleyViolinInteractor


def get_hartley_repository(db: AsyncSession = Depends(get_db)) -> HartleyViolinPort:
    return HartleyViolinRepository(session=db)


def get_hartley_use_case(
    repository: HartleyViolinPort = Depends(get_hartley_repository),
) -> HartleyUseCase:
    return HartleyViolinInteractor(repository=repository)
