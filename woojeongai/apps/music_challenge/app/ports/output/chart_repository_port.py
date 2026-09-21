from abc import ABC, abstractmethod

from music_challenge.domain.entities.chart_entity import ChallengeChart


class ChartRepositoryPort(ABC):
    @abstractmethod
    async def find(self, challenge_id: int) -> ChallengeChart | None: ...

    @abstractmethod
    async def save(self, chart: ChallengeChart) -> ChallengeChart:
        """있으면 덮어쓰고 없으면 만든다."""
