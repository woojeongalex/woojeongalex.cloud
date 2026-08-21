from abc import ABC, abstractmethod

from music_challenge.app.dtos.evaluation_dto import EvaluationResult
from music_challenge.app.dtos.submission_dto import SubmitChallengeCommand


class SubmitChallengeUseCase(ABC):
    @abstractmethod
    async def submit(self, command: SubmitChallengeCommand) -> EvaluationResult: ...
