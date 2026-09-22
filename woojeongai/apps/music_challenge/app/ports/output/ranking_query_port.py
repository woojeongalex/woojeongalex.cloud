from abc import ABC, abstractmethod
from datetime import datetime

from music_challenge.app.dtos.ranking_dto import (
    MyStanding,
    RankingEntry,
    WeeklyRankingEntry,
)


class RankingQueryPort(ABC):
    """노래방·연주 랭킹 읽기 모델. 한 사람은 자기 최고 기록 하나로만 오른다."""

    @abstractmethod
    async def challenge_ranking(
        self, challenge_id: int, limit: int
    ) -> list[RankingEntry]: ...

    @abstractmethod
    async def my_standing(self, challenge_id: int, user_id: int) -> MyStanding | None:
        """기록이 없으면 None."""

    @abstractmethod
    async def weekly_ranking(
        self, since: datetime, limit: int
    ) -> list[WeeklyRankingEntry]:
        """since 이후 기록 중 사람마다 가장 높은 한 곡."""
