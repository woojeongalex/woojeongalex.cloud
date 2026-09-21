from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import (
    ChallengeSubmissionModel,
    MusicChallengeModel,
    SubmissionEvaluationModel,
)
from music_challenge.app.dtos.history_dto import SubmissionHistoryItem
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

    async def find_attempted_challenge_ids(self, user_id: int) -> set[int]:
        result = await self._session.execute(
            select(ChallengeSubmissionModel.challenge_id)
            .where(ChallengeSubmissionModel.user_id == user_id)
            .distinct()
        )
        return set(result.scalars())

    def _to_entity(self, model: ChallengeSubmissionModel) -> ChallengeSubmission:
        return ChallengeSubmission(
            id=model.id,
            challenge_id=model.challenge_id,
            user_id=model.user_id,
            media_type=MediaType(model.media_type),
            s3_key=model.s3_key,
            created_at=model.created_at,
        )

    async def find_history_by_user(
        self, user_id: int, limit: int
    ) -> list[SubmissionHistoryItem]:
        # 평가가 없는 제출도 기록에는 남아야 하므로 outerjoin.
        stmt = (
            select(
                ChallengeSubmissionModel.id,
                ChallengeSubmissionModel.challenge_id,
                MusicChallengeModel.title,
                MusicChallengeModel.challenge_type,
                ChallengeSubmissionModel.media_type,
                ChallengeSubmissionModel.created_at,
                SubmissionEvaluationModel.score,
                SubmissionEvaluationModel.pitch_score,
                SubmissionEvaluationModel.rhythm_score,
            )
            .join(
                MusicChallengeModel,
                MusicChallengeModel.id == ChallengeSubmissionModel.challenge_id,
            )
            .outerjoin(
                SubmissionEvaluationModel,
                SubmissionEvaluationModel.submission_id == ChallengeSubmissionModel.id,
            )
            .where(ChallengeSubmissionModel.user_id == user_id)
            .order_by(ChallengeSubmissionModel.id.desc())
            .limit(limit)
        )
        rows = await self._session.execute(stmt)
        return [
            SubmissionHistoryItem(
                submission_id=r[0],
                challenge_id=r[1],
                challenge_title=r[2],
                challenge_type=r[3],
                media_type=r[4],
                created_at=r[5],
                score=r[6],
                pitch_score=r[7],
                rhythm_score=r[8],
            )
            for r in rows.all()
        ]
