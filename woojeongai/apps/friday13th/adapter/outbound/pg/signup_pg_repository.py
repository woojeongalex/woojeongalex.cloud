from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from friday13th.app.ports.output.signup_repository_port import SignupRepositoryPort
from friday13th.domain.entities.friday13th import UserAccount
from friday13th.adapter.outbound.orm.user_model import (
    UserEntity,
    hash_password,
)


class SignupPgRepository(SignupRepositoryPort):
    def __init__(self, db: AsyncSession | None = None) -> None:
        self._db = db

    def _require_db(self) -> AsyncSession:
        if self._db is None:
            raise RuntimeError("DB session is not available.")
        return self._db

    async def exists_by_username(self, username: str) -> bool:
        db = self._require_db()
        stmt = select(UserEntity.id).where(func.lower(UserEntity.username) == username.strip().lower())
        return (await db.execute(stmt)).scalar_one_or_none() is not None

    async def exists_by_nickname(self, nickname: str) -> bool:
        db = self._require_db()
        stmt = select(UserEntity.id).where(func.lower(UserEntity.nickname) == nickname.strip().lower())
        return (await db.execute(stmt)).scalar_one_or_none() is not None

    async def save_user(self, account: UserAccount) -> None:
        db = self._require_db()
        entity = UserEntity(
            username=account.username.strip(),
            nickname=account.nickname.strip(),
            email=account.email.strip(),
            password_hash=hash_password(account.password),
            role="user",
        )
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
