from friday13th.app.ports.input.signup_use_case import SignupUseCase
from friday13th.app.ports.output.signup_repository_port import SignupRepositoryPort
from friday13th.domain.entities.friday13th import UserAccount


class SignupInteractor(SignupUseCase):
    def __init__(self, repository: SignupRepositoryPort) -> None:
        self._repository = repository

    async def signup(self, account: UserAccount, password_confirm: str | None = None) -> None:
        if password_confirm is not None and account.password != password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        if await self._repository.exists_by_username(account.username):
            raise ValueError("이미 사용 중인 아이디입니다.")
        if await self._repository.exists_by_nickname(account.nickname):
            raise ValueError("이미 사용 중인 닉네임입니다.")
        await self._repository.save_user(account)

    async def is_username_available(self, username: str) -> bool:
        normalized = username.strip()
        if not normalized:
            raise ValueError("아이디를 입력하세요.")
        return not await self._repository.exists_by_username(normalized)

    async def is_nickname_available(self, nickname: str) -> bool:
        normalized = nickname.strip()
        if not normalized:
            raise ValueError("닉네임을 입력하세요.")
        return not await self._repository.exists_by_nickname(normalized)
