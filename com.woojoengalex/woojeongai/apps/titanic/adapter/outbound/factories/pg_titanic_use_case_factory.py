"""[Layer: Interface Adapters] PG 기반 TitanicUseCaseFactory 구현."""

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.repositories.crew_james_repository import JamesRepository
from titanic.app.factories.titanic_use_case_factory import TitanicUseCaseFactory
from titanic.app.ports.input.crew_james_use_case import JamesUseCase
from titanic.app.ports.input.crew_walter_use_case import WalterUseCase
from titanic.app.use_cases.crew_james_director_interactor import JamesDirectorInteractor
from titanic.app.use_cases.crew_walter_interactor import WalterInteractor
from titanic.adapter.outbound.repositories.crew_walter_repository import WalterRepository


class PgTitanicUseCaseFactory(TitanicUseCaseFactory):
    db: AsyncSession

    @staticmethod
    def create_james_use_case() -> JamesUseCase:
        return JamesDirectorInteractor(JamesRepository(PgTitanicUseCaseFactory.db))

    @staticmethod
    def create_walter_use_case() -> WalterUseCase:
        return WalterInteractor(WalterRepository(PgTitanicUseCaseFactory.db))
