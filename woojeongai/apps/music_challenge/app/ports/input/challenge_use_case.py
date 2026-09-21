from abc import ABC, abstractmethod

from music_challenge.app.dtos.challenge_dto import (
    ChallengeResult,
    CreateChallengeCommand,
)


class CreateChallengeUseCase(ABC):
    @abstractmethod
    async def create(self, command: CreateChallengeCommand) -> ChallengeResult: ...


class ListChallengesUseCase(ABC):
    @abstractmethod
    async def list_active(self) -> list[ChallengeResult]: ...


class GetChallengeUseCase(ABC):
    @abstractmethod
    async def get(self, challenge_id: int) -> ChallengeResult: ...
