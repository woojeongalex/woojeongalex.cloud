from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import MusicChallengeModel
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.domain.entities.challenge_entity import MusicChallenge
from music_challenge.domain.value_objects.music_challenge_vo import ChallengeType


class ChallengePgRepository(ChallengeRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, challenge: MusicChallenge) -> MusicChallenge:
        model = MusicChallengeModel(
            title=challenge.title,
            description=challenge.description,
            music_s3_key=challenge.music_s3_key,
            challenge_type=challenge.challenge_type.value,
            is_active=challenge.is_active,
            created_at=challenge.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, challenge_id: int) -> MusicChallenge | None:
        model = await self._session.get(MusicChallengeModel, challenge_id)
        return self._to_entity(model) if model else None

    async def find_all_active(self) -> list[MusicChallenge]:
        stmt = select(MusicChallengeModel).where(MusicChallengeModel.is_active == True)
        rows = await self._session.execute(stmt)
        return [self._to_entity(r) for r in rows.scalars()]

    def _to_entity(self, model: MusicChallengeModel) -> MusicChallenge:
        return MusicChallenge(
            id=model.id,
            title=model.title,
            description=model.description,
            music_s3_key=model.music_s3_key,
            challenge_type=ChallengeType(model.challenge_type),
            is_active=model.is_active,
            created_at=model.created_at,
        )
