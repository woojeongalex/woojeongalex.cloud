from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from friday13th.adapter.outbound.orm.user_model import UserEntity
from music_challenge.app.ports.output.user_lookup_port import UserLookupPort


class UserLookupPgRepository(UserLookupPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_id_by_username(self, username: str) -> int | None:
        normalized = (username or "").strip()
        if not normalized:
            return None
        result = await self._session.execute(
            select(UserEntity.id).where(UserEntity.username == normalized)
        )
        return result.scalar_one_or_none()
