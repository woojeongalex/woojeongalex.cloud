from abc import ABC, abstractmethod

from music_challenge.app.dtos.history_dto import SubmissionHistoryItem
from music_challenge.domain.entities.submission_entity import ChallengeSubmission


class SubmissionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, submission: ChallengeSubmission) -> ChallengeSubmission: ...

    @abstractmethod
    async def find_by_id(self, submission_id: int) -> ChallengeSubmission | None: ...

    @abstractmethod
    async def find_attempted_challenge_ids(self, user_id: int) -> set[int]:
        """해당 사용자가 한 번이라도 제출한 챌린지 id 집합.

        추천에서 이미 해본 챌린지를 빼기 위해 쓴다.
        """
        ...

    @abstractmethod
    async def find_history_by_user(
        self, user_id: int, limit: int
    ) -> list[SubmissionHistoryItem]:
        """최신순 도전 기록. 제출·챌린지·평가를 합친 읽기 모델을 돌려준다."""
        ...
