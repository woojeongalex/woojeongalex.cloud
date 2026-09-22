from abc import ABC, abstractmethod

from music_challenge.app.dtos.ranking_dto import (
    MyStanding,
    RankingEntry,
    WeeklyRankingEntry,
)


class GetChallengeRankingUseCase(ABC):
    @abstractmethod
    async def get(
        self, challenge_id: int, limit: int, username: str | None
    ) -> tuple[list[RankingEntry], MyStanding | None]:
        """곡별 랭킹과, 로그인했다면 내 순위."""


class GetWeeklyRankingUseCase(ABC):
    @abstractmethod
    async def get(self, limit: int) -> list[WeeklyRankingEntry]: ...
