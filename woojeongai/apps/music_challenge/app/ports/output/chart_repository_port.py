from abc import ABC, abstractmethod
from dataclasses import dataclass

from music_challenge.domain.entities.chart_entity import ChallengeChart


@dataclass(frozen=True)
class ChartSummary:
    """추천에 쓰는 악보 요약. 음표 전체를 들고 다니지 않으려고 음역만 남긴다."""

    challenge_id: int
    low_midi: float
    high_midi: float


class ChartRepositoryPort(ABC):
    @abstractmethod
    async def find(self, challenge_id: int) -> ChallengeChart | None: ...

    @abstractmethod
    async def save(self, chart: ChallengeChart) -> ChallengeChart:
        """있으면 덮어쓰고 없으면 만든다."""

    @abstractmethod
    async def find_ready_summaries(self) -> list[ChartSummary]:
        """부를 수 있는 악보만. 추천이 악보 없는 곡을 고르지 않게 하는 데 쓴다."""
