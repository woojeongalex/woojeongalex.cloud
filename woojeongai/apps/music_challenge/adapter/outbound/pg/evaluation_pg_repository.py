from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import (
    SubmissionEvaluationModel,
)
from music_challenge.app.ports.output.evaluation_repository_port import (
    EvaluationRepositoryPort,
)
from music_challenge.domain.entities.evaluation_entity import SubmissionEvaluation


class EvaluationPgRepository(EvaluationRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, evaluation: SubmissionEvaluation) -> SubmissionEvaluation:
        model = SubmissionEvaluationModel(
            submission_id=evaluation.submission_id,
            score=evaluation.score,
            feedback=evaluation.feedback,
            next_challenge_id=evaluation.next_challenge_id,
            created_at=evaluation.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_submission_id(self, submission_id: int) -> SubmissionEvaluation | None:
        stmt = select(SubmissionEvaluationModel).where(
            SubmissionEvaluationModel.submission_id == submission_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: SubmissionEvaluationModel) -> SubmissionEvaluation:
        return SubmissionEvaluation(
            id=model.id,
            submission_id=model.submission_id,
            score=model.score,
            feedback=model.feedback,
            next_challenge_id=model.next_challenge_id,
            created_at=model.created_at,
        )
