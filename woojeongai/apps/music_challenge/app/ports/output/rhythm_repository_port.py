from abc import ABC, abstractmethod

from music_challenge.app.dtos.rhythm_dto import (
    RhythmChartBrief,
    RhythmRankingEntry,
    RhythmStanding,
)
from music_challenge.domain.entities.rhythm_entity import RhythmChart, RhythmPlay
from music_challenge.domain.value_objects.rhythm_vo import RhythmDifficulty


class RhythmChartRepositoryPort(ABC):
    @abstractmethod
    async def find(self, challenge_id: int) -> RhythmChart | None: ...

    @abstractmethod
    async def save(self, chart: RhythmChart) -> RhythmChart:
        """있으면 덮어쓰고 없으면 만든다."""


class RhythmPlayRepositoryPort(ABC):
    @abstractmethod
    async def save(self, play: RhythmPlay) -> RhythmPlay: ...


class RhythmRankingQueryPort(ABC):
    """채보(곡·키 수·난이도)별 랭킹. 한 사람은 자기 최고 기록 하나로만 오른다."""

    @abstractmethod
    async def ranking(
        self, challenge_id: int, keys: int, difficulty: RhythmDifficulty, limit: int
    ) -> list[RhythmRankingEntry]: ...

    @abstractmethod
    async def my_standing(
        self, challenge_id: int, keys: int, difficulty: RhythmDifficulty, user_id: int
    ) -> RhythmStanding | None:
        """기록이 없으면 None."""


class RhythmChartListQueryPort(ABC):
    @abstractmethod
    async def list_ready(self) -> list[RhythmChartBrief]:
        """채보가 준비된 곡들의 요약. 노트는 싣지 않는다(곡마다 수천 개라서)."""
