from abc import ABC, abstractmethod

from music_challenge.domain.entities.submission_entity import ChallengeSubmission


class SubmissionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, submission: ChallengeSubmission) -> ChallengeSubmission: ...

    @abstractmethod
    async def find_by_id(self, submission_id: int) -> ChallengeSubmission | None: ...
