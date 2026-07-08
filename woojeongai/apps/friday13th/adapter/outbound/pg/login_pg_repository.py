from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from friday13th.adapter.outbound.orm.user_model import UserEntity, verify_password
from friday13th.app.dtos.login_result import LoginResultDto
from friday13th.app.ports.output.login_repository_port import LoginRepositoryPort


class LoginPgRepository(LoginRepositoryPort):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def login(self, username: str, password: str) -> LoginResultDto:
        stmt = select(UserEntity).where(
            func.lower(UserEntity.username) == username.strip().lower()
        )
        row = (await self._db.execute(stmt)).scalar_one_or_none()
        if row is None or not verify_password(password, row.password_hash):
            raise ValueError("아이디 또는 비밀번호가 올바르지 않습니다.")
        return LoginResultDto(
            ok=True,
            message="로그인되었습니다.",
            username=row.username,
            nickname=row.nickname,
            role=row.role,
        )
