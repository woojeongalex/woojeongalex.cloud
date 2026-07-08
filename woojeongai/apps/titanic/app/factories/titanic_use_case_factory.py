"""[Layer: Application] Titanic Use Case 팩토리 추상."""

from abc import ABC, abstractmethod
from titanic.app.ports.input.crew_james_use_case import JamesUseCase
from titanic.app.ports.input.crew_walter_use_case import WalterUseCase


class TitanicUseCaseFactory(ABC):
    @staticmethod
    @abstractmethod
    def create_james_use_case() -> JamesUseCase:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_walter_use_case() -> WalterUseCase:
        raise NotImplementedError
