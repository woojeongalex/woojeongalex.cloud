"""[Layer: Interface Adapters] PG 기반 SiliconValleyUseCaseFactory 구현."""

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.adapter.outbound.repositories.piper_bighetti_hr_repository import BighettiHrRepository
from silicon_valley.adapter.outbound.repositories.piper_hendricks__ceo_repository import HendricksCeoRepository
from silicon_valley.app.factories.silicon_valley_use_case_factory import SiliconValleyUseCaseFactory
from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import HendricksCeoUseCase
from silicon_valley.app.use_cases.piper_bighetti_hr_interactor import BighettiHrInteractor
from silicon_valley.app.use_cases.piper_hendricks__ceo_interactor import HendricksCeoInteractor


class PgSiliconValleyUseCaseFactory(SiliconValleyUseCaseFactory):
    db: AsyncSession

    @staticmethod
    def create_bighetti_hr_use_case() -> BighettiHrUseCase:
        return BighettiHrInteractor(BighettiHrRepository(PgSiliconValleyUseCaseFactory.db))

    @staticmethod
    def create_hendricks_ceo_use_case() -> HendricksCeoUseCase:
        return HendricksCeoInteractor(HendricksCeoRepository(PgSiliconValleyUseCaseFactory.db))
