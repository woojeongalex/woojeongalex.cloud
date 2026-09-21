import asyncio
import uuid
from datetime import datetime

from fastapi import HTTPException

from music_challenge.app.dtos.evaluation_dto import EvaluationResult
from music_challenge.app.dtos.submission_dto import SubmitChallengeCommand
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.app.ports.output.ai_evaluator_port import AIEvaluatorPort
from music_challenge.app.ports.output.audio_analysis_port import AudioAnalysisPort
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.evaluation_repository_port import (
    EvaluationRepositoryPort,
)
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.ports.output.submission_repository_port import (
    SubmissionRepositoryPort,
)
from music_challenge.app.ports.output.user_lookup_port import UserLookupPort
from music_challenge.domain.entities.challenge_entity import MusicChallenge
from music_challenge.domain.entities.evaluation_entity import SubmissionEvaluation
from music_challenge.domain.entities.submission_entity import ChallengeSubmission

# 이 점수 미만이면 "같은 유형 더 연습", 이상이면 "다른 유형으로 확장"
_PRACTICE_MORE_BELOW = 60


class SubmitChallengeInteractor(SubmitChallengeUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        submission_repo: SubmissionRepositoryPort,
        evaluation_repo: EvaluationRepositoryPort,
        storage: MediaStoragePort,
        evaluator: AIEvaluatorPort,
        user_lookup: UserLookupPort,
        audio_analysis: AudioAnalysisPort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._submission_repo = submission_repo
        self._evaluation_repo = evaluation_repo
        self._storage = storage
        self._evaluator = evaluator
        self._user_lookup = user_lookup
        self._audio_analysis = audio_analysis

    async def submit(self, command: SubmitChallengeCommand) -> EvaluationResult:
        challenge = await self._challenge_repo.find_by_id(command.challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        # 클라이언트가 보낸 id 를 믿지 않는다. 검증된 토큰의 username 으로만 조회한다.
        user_id = (
            await self._user_lookup.find_id_by_username(command.username)
            if command.username
            else None
        )

        key = f"music_challenge/submissions/{uuid.uuid4()}_{command.filename}"
        await self._storage.upload(key, command.data, command.content_type)

        saved_sub = await self._submission_repo.save(
            ChallengeSubmission(
                id=0,
                challenge_id=command.challenge_id,
                user_id=user_id,
                media_type=command.media_type,
                s3_key=key,
                created_at=datetime.utcnow(),
            )
        )

        # librosa 분석은 CPU-bound 동기 함수라 이벤트 루프를 막지 않게 위임한다.
        metrics = await asyncio.to_thread(
            self._audio_analysis.analyze, command.data, command.content_type
        )

        score, feedback = await self._evaluator.evaluate(
            challenge_title=challenge.title,
            challenge_description=challenge.description,
            challenge_type=challenge.challenge_type,
            media_bytes=command.data,
            media_type=command.media_type,
            content_type=command.content_type,
            metrics=metrics,
        )

        all_active = await self._challenge_repo.find_all_active()
        attempted = (
            await self._submission_repo.find_attempted_challenge_ids(user_id)
            if user_id
            else set()
        )
        next_id = self._recommend_next(challenge, score, all_active, attempted)

        saved_eval = await self._evaluation_repo.save(
            SubmissionEvaluation(
                id=0,
                submission_id=saved_sub.id,
                score=score,
                feedback=feedback,
                next_challenge_id=next_id,
                pitch_score=metrics.pitch_score if metrics else None,
                rhythm_score=metrics.rhythm_score if metrics else None,
                tempo=metrics.tempo if metrics else None,
                created_at=datetime.utcnow(),
            )
        )

        return EvaluationResult(
            id=saved_eval.id,
            submission_id=saved_eval.submission_id,
            score=saved_eval.score,
            feedback=saved_eval.feedback,
            next_challenge_id=saved_eval.next_challenge_id,
            pitch_score=saved_eval.pitch_score,
            rhythm_score=saved_eval.rhythm_score,
            tempo=saved_eval.tempo,
        )

    def _recommend_next(
        self,
        current: MusicChallenge,
        score: int,
        all_active: list[MusicChallenge],
        attempted: set[int],
    ) -> int | None:
        """다음에 도전할 챌린지를 고른다.

        규칙은 단순하지만 근거가 있다.
        1. 방금 푼 것과 이미 해본 것은 뺀다(로그인 사용자만 이력을 안다).
        2. 점수가 낮으면 같은 유형으로 더 연습시키고, 높으면 다른 유형으로
           넓혀준다. 잘한 사람에게 같은 걸 또 주면 지루하고, 못한 사람에게
           낯선 유형을 주면 이탈한다.
        3. 후보가 없으면(다 해봤으면) 방금 것만 빼고 재도전을 권한다.
        """
        fresh = [c for c in all_active if c.id != current.id and c.id not in attempted]
        candidates = fresh or [c for c in all_active if c.id != current.id]
        if not candidates:
            return None

        if score < _PRACTICE_MORE_BELOW:
            same_type = [
                c for c in candidates if c.challenge_type == current.challenge_type
            ]
            if same_type:
                return same_type[0].id
        else:
            other_type = [
                c for c in candidates if c.challenge_type != current.challenge_type
            ]
            if other_type:
                return other_type[0].id

        return candidates[0].id
