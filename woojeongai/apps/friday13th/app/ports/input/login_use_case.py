"""[Layer: Ports] 로그인 입력 Port."""

from abc import ABC, abstractmethod

from friday13th.app.dtos.login_result import LoginResultDto


class LoginUseCase(ABC):
    @abstractmethod
    async def login(self, username: str, password: str) -> LoginResultDto:
        pass
