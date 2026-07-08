from friday13th.app.dtos.login_result import LoginResultDto
from friday13th.app.ports.input.login_use_case import LoginUseCase
from friday13th.app.ports.output.login_repository_port import LoginRepositoryPort


class LoginInteractor(LoginUseCase):
    def __init__(self, repository: LoginRepositoryPort) -> None:
        self._repository = repository

    async def login(self, username: str, password: str) -> LoginResultDto:
        if not username.strip() or not password:
            raise ValueError("아이디와 비밀번호를 입력하세요.")
        return await self._repository.login(username, password)
