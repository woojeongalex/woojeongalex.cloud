from abc import ABC, abstractmethod

from friday13th.domain.entities.friday13th import UserAccount


class SignupRepositoryPort(ABC):
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        pass

    @abstractmethod
    async def exists_by_nickname(self, nickname: str) -> bool:
        pass

    @abstractmethod
    async def save_user(self, account: UserAccount) -> None:
        pass
