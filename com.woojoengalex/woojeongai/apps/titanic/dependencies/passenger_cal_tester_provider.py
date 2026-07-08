from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.repositories.passenger_cal_tester_repository import CalTestRepository
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTestUseCase
from titanic.app.ports.output.passenger_cal_tester_port import CalTestPort
from titanic.app.use_cases.passenger_cal_tester_interactor import CalTestInteractor


def get_cal_test_repository(db: AsyncSession = Depends(get_db)) -> CalTestPort:
    return CalTestRepository(session=db)


def get_cal_test_use_case(
    repository: CalTestPort = Depends(get_cal_test_repository)
) -> CalTestUseCase:
    return CalTestInteractor(repository=repository)
