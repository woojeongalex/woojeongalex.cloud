from abc import ABC, abstractmethod

from music_challenge.domain.entities.evaluation_entity import SubmissionEvaluation


class EvaluationRepositoryPort(ABC):
    @abstractmethod
    async def save(self, evaluation: SubmissionEvaluation) -> SubmissionEvaluation: ...

    @abstractmethod
    async def find_by_submission_id(
        self, submission_id: int
    ) -> SubmissionEvaluation | None: ...
