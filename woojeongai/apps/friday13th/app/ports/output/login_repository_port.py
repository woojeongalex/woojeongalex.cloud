"""[Layer: Ports] 로그인 출력 Port — 인증 조회·검증 계약."""

from abc import ABC, abstractmethod

from friday13th.app.dtos.login_result import LoginResultDto


class LoginRepositoryPort(ABC):
    @abstractmethod
    async def login(self, username: str, password: str) -> LoginResultDto:
        pass
