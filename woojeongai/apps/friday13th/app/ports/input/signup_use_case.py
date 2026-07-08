from abc import ABC, abstractmethod

from friday13th.domain.entities.friday13th import UserAccount


class SignupUseCase(ABC):
    @abstractmethod
    async def signup(self, account: UserAccount, password_confirm: str | None = None) -> None:
        pass

    @abstractmethod
    async def is_username_available(self, username: str) -> bool:
        pass

    @abstractmethod
    async def is_nickname_available(self, nickname: str) -> bool:
        pass
