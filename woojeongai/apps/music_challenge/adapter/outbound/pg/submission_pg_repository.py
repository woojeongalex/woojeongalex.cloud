from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import (
    ChallengeSubmissionModel,
)
from music_challenge.app.ports.output.submission_repository_port import (
    SubmissionRepositoryPort,
)
from music_challenge.domain.entities.submission_entity import ChallengeSubmission
from music_challenge.domain.value_objects.music_challenge_vo import MediaType


class SubmissionPgRepository(SubmissionRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, submission: ChallengeSubmission) -> ChallengeSubmission:
        model = ChallengeSubmissionModel(
            challenge_id=submission.challenge_id,
            user_id=submission.user_id,
            media_type=submission.media_type.value,
            s3_key=submission.s3_key,
            created_at=submission.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, submission_id: int) -> ChallengeSubmission | None:
        model = await self._session.get(ChallengeSubmissionModel, submission_id)
        return self._to_entity(model) if model else None

    def _to_entity(self, model: ChallengeSubmissionModel) -> ChallengeSubmission:
        return ChallengeSubmission(
            id=model.id,
            challenge_id=model.challenge_id,
            user_id=model.user_id,
            media_type=MediaType(model.media_type),
            s3_key=model.s3_key,
            created_at=model.created_at,
        )
