from abc import ABC, abstractmethod

from music_challenge.domain.entities.challenge_entity import MusicChallenge


class ChallengeRepositoryPort(ABC):
    @abstractmethod
    async def save(self, challenge: MusicChallenge) -> MusicChallenge: ...

    @abstractmethod
    async def find_by_id(self, challenge_id: int) -> MusicChallenge | None: ...

    @abstractmethod
    async def find_all_active(self) -> list[MusicChallenge]: ...
