"""[Layer: Application] Silicon Valley Use Case 팩토리 추상."""

from abc import ABC, abstractmethod

from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import HendricksCeoUseCase


class SiliconValleyUseCaseFactory(ABC):
    @staticmethod
    @abstractmethod
    def create_bighetti_hr_use_case() -> BighettiHrUseCase:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_hendricks_ceo_use_case() -> HendricksCeoUseCase:
        raise NotImplementedError
