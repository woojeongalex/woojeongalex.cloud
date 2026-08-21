import uuid
from datetime import datetime

from fastapi import HTTPException

from music_challenge.app.dtos.evaluation_dto import EvaluationResult
from music_challenge.app.dtos.submission_dto import SubmitChallengeCommand
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.app.ports.output.ai_evaluator_port import AIEvaluatorPort
from music_challenge.app.ports.output.challenge_repository_port import ChallengeRepositoryPort
from music_challenge.app.ports.output.evaluation_repository_port import EvaluationRepositoryPort
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.ports.output.submission_repository_port import SubmissionRepositoryPort
from music_challenge.domain.entities.evaluation_entity import SubmissionEvaluation
from music_challenge.domain.entities.submission_entity import ChallengeSubmission


class SubmitChallengeInteractor(SubmitChallengeUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        submission_repo: SubmissionRepositoryPort,
        evaluation_repo: EvaluationRepositoryPort,
        storage: MediaStoragePort,
        evaluator: AIEvaluatorPort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._submission_repo = submission_repo
        self._evaluation_repo = evaluation_repo
        self._storage = storage
        self._evaluator = evaluator

    async def submit(self, command: SubmitChallengeCommand) -> EvaluationResult:
        challenge = await self._challenge_repo.find_by_id(command.challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        key = f"music_challenge/submissions/{uuid.uuid4()}_{command.filename}"
        await self._storage.upload(key, command.data, command.content_type)

        saved_sub = await self._submission_repo.save(
            ChallengeSubmission(
                id=0,
                challenge_id=command.challenge_id,
                media_type=command.media_type,
                s3_key=key,
                created_at=datetime.utcnow(),
            )
        )

        score, feedback = await self._evaluator.evaluate(
            challenge_title=challenge.title,
            challenge_description=challenge.description,
            challenge_type=challenge.challenge_type,
            media_bytes=command.data,
            media_type=command.media_type,
            content_type=command.content_type,
        )

        all_active = await self._challenge_repo.find_all_active()
        next_id = next(
            (c.id for c in all_active if c.id != command.challenge_id),
            None,
        )

        saved_eval = await self._evaluation_repo.save(
            SubmissionEvaluation(
                id=0,
                submission_id=saved_sub.id,
                score=score,
                feedback=feedback,
                next_challenge_id=next_id,
                created_at=datetime.utcnow(),
            )
        )

        return EvaluationResult(
            id=saved_eval.id,
            submission_id=saved_eval.submission_id,
            score=saved_eval.score,
            feedback=saved_eval.feedback,
            next_challenge_id=saved_eval.next_challenge_id,
        )
