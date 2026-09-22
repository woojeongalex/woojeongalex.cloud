"""노래방·연주 랭킹 — PostgreSQL 읽기 쿼리.

한 사람이 여러 번 도전해도 랭킹에는 가장 높은 기록 하나만 오른다.
같은 점수면 먼저 달성한 사람이 위에 보이고, 순위 숫자는 같이 나눈다(RANK).
비로그인 제출(user_id 없음)과 일반 제출(karaoke_score 없음)은 빠진다.
"""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.app.dtos.ranking_dto import (
    MyStanding,
    RankingEntry,
    WeeklyRankingEntry,
)
from music_challenge.app.ports.output.ranking_query_port import RankingQueryPort

# 사람마다 최고 기록 한 줄 — 같은 점수가 여러 번이면 가장 먼저 달성한 것
_BEST_PER_USER = """
    SELECT DISTINCT ON (s.user_id)
        s.user_id,
        e.karaoke_score AS score,
        e.karaoke_pitch_accuracy AS pitch_accuracy,
        e.karaoke_timing_accuracy AS timing_accuracy,
        e.created_at AS achieved_at
    FROM submission_evaluations e
    JOIN challenge_submissions s ON s.id = e.submission_id
    WHERE s.challenge_id = :challenge_id
      AND s.user_id IS NOT NULL
      AND e.karaoke_score IS NOT NULL
    ORDER BY s.user_id, e.karaoke_score DESC, e.created_at ASC
"""

_CHALLENGE_RANKING = text(
    f"""
    WITH best AS ({_BEST_PER_USER})
    SELECT RANK() OVER (ORDER BY b.score DESC) AS rank,
           u.nickname, b.score, b.pitch_accuracy, b.timing_accuracy, b.achieved_at
    FROM best b
    JOIN users u ON u.id = b.user_id
    ORDER BY b.score DESC, b.achieved_at ASC
    LIMIT :limit
    """
)

_MY_STANDING = text(
    f"""
    WITH best AS ({_BEST_PER_USER})
    SELECT me.score AS best_score,
           1 + (SELECT COUNT(*) FROM best other WHERE other.score > me.score) AS rank
    FROM best me
    WHERE me.user_id = :user_id
    """
)

_WEEKLY_RANKING = text(
    """
    WITH best AS (
        SELECT DISTINCT ON (s.user_id)
            s.user_id,
            s.challenge_id,
            e.karaoke_score AS score,
            e.karaoke_pitch_accuracy AS pitch_accuracy,
            e.karaoke_timing_accuracy AS timing_accuracy,
            e.created_at AS achieved_at
        FROM submission_evaluations e
        JOIN challenge_submissions s ON s.id = e.submission_id
        WHERE e.created_at >= :since
          AND s.user_id IS NOT NULL
          AND e.karaoke_score IS NOT NULL
        ORDER BY s.user_id, e.karaoke_score DESC, e.created_at ASC
    )
    SELECT RANK() OVER (ORDER BY b.score DESC) AS rank,
           u.nickname, b.score, b.pitch_accuracy, b.timing_accuracy, b.achieved_at,
           b.challenge_id, c.title AS challenge_title
    FROM best b
    JOIN users u ON u.id = b.user_id
    JOIN music_challenges c ON c.id = b.challenge_id
    ORDER BY b.score DESC, b.achieved_at ASC
    LIMIT :limit
    """
)


class RankingPgQuery(RankingQueryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def challenge_ranking(
        self, challenge_id: int, limit: int
    ) -> list[RankingEntry]:
        rows = await self._session.execute(
            _CHALLENGE_RANKING, {"challenge_id": challenge_id, "limit": limit}
        )
        return [
            RankingEntry(
                rank=int(r.rank),
                nickname=r.nickname,
                score=int(r.score),
                pitch_accuracy=r.pitch_accuracy,
                timing_accuracy=r.timing_accuracy,
                achieved_at=r.achieved_at,
            )
            for r in rows
        ]

    async def my_standing(self, challenge_id: int, user_id: int) -> MyStanding | None:
        row = (
            await self._session.execute(
                _MY_STANDING, {"challenge_id": challenge_id, "user_id": user_id}
            )
        ).first()
        if row is None:
            return None
        return MyStanding(rank=int(row.rank), best_score=int(row.best_score))

    async def weekly_ranking(
        self, since: datetime, limit: int
    ) -> list[WeeklyRankingEntry]:
        rows = await self._session.execute(
            _WEEKLY_RANKING, {"since": since, "limit": limit}
        )
        return [
            WeeklyRankingEntry(
                rank=int(r.rank),
                nickname=r.nickname,
                score=int(r.score),
                pitch_accuracy=r.pitch_accuracy,
                timing_accuracy=r.timing_accuracy,
                achieved_at=r.achieved_at,
                challenge_id=int(r.challenge_id),
                challenge_title=r.challenge_title,
            )
            for r in rows
        ]
