from datetime import datetime, timedelta

from music_challenge.app.dtos.ranking_dto import WeeklyRankingEntry
from music_challenge.app.ports.input.ranking_use_case import GetWeeklyRankingUseCase
from music_challenge.app.ports.output.ranking_query_port import RankingQueryPort

# 한국 시간 기준 월요일 0시부터가 "이번 주"다. DB 시각은 UTC(naive)로 저장된다.
_KST = timedelta(hours=9)


def week_start_utc(now_utc: datetime) -> datetime:
    kst = now_utc + _KST
    monday = (kst - timedelta(days=kst.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return monday - _KST


class GetWeeklyRankingInteractor(GetWeeklyRankingUseCase):
    def __init__(self, ranking: RankingQueryPort) -> None:
        self._ranking = ranking

    async def get(self, limit: int) -> list[WeeklyRankingEntry]:
        return await self._ranking.weekly_ranking(
            week_start_utc(datetime.utcnow()), limit
        )
