"""리듬 게임 채보·플레이 저장과 채보별 랭킹 쿼리."""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import (
    RhythmChartModel,
    RhythmPlayModel,
)
from music_challenge.app.dtos.rhythm_dto import RhythmRankingEntry, RhythmStanding
from music_challenge.app.ports.output.rhythm_repository_port import (
    RhythmChartRepositoryPort,
    RhythmPlayRepositoryPort,
    RhythmRankingQueryPort,
)
from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.entities.rhythm_entity import RhythmChart, RhythmPlay
from music_challenge.domain.value_objects.rhythm_vo import (
    RhythmDifficulty,
    RhythmNote,
    RhythmSheet,
)


def _sheet_to_json(sheet: RhythmSheet) -> dict:
    return {
        "keys": sheet.keys,
        "difficulty": sheet.difficulty.value,
        "level": sheet.level,
        "notes": [[n.time, n.lane, n.end] for n in sheet.notes],
    }


def _sheet_from_json(raw: dict) -> RhythmSheet:
    return RhythmSheet(
        keys=int(raw["keys"]),
        difficulty=RhythmDifficulty(raw["difficulty"]),
        level=int(raw["level"]),
        notes=[
            RhythmNote(time=t, lane=int(lane), end=end) for t, lane, end in raw["notes"]
        ],
    )


class RhythmChartPgRepository(RhythmChartRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find(self, challenge_id: int) -> RhythmChart | None:
        model = await self._session.get(RhythmChartModel, challenge_id)
        return self._to_entity(model) if model else None

    async def save(self, chart: RhythmChart) -> RhythmChart:
        model = await self._session.get(RhythmChartModel, chart.challenge_id)
        if model is None:
            model = RhythmChartModel(challenge_id=chart.challenge_id)
            self._session.add(model)
        model.status = chart.status.value
        model.job_id = chart.job_id
        model.bpm = chart.bpm
        model.duration = chart.duration
        model.sheets = [_sheet_to_json(s) for s in chart.sheets] or None
        model.error = chart.error
        model.updated_at = datetime.utcnow()
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: RhythmChartModel) -> RhythmChart:
        return RhythmChart(
            challenge_id=model.challenge_id,
            status=ChartStatus(model.status),
            job_id=model.job_id,
            bpm=model.bpm,
            duration=model.duration,
            sheets=[_sheet_from_json(s) for s in (model.sheets or [])],
            error=model.error,
            updated_at=model.updated_at,
        )


class RhythmPlayPgRepository(RhythmPlayRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, play: RhythmPlay) -> RhythmPlay:
        model = RhythmPlayModel(
            challenge_id=play.challenge_id,
            user_id=play.user_id,
            keys=play.keys,
            difficulty=play.difficulty.value,
            score=play.score,
            accuracy=play.accuracy,
            max_combo=play.max_combo,
            cool=play.cool,
            good=play.good,
            bad=play.bad,
            miss=play.miss,
            created_at=play.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return RhythmPlay(
            id=model.id or 0,
            challenge_id=model.challenge_id,
            user_id=model.user_id,
            keys=model.keys,
            difficulty=RhythmDifficulty(model.difficulty),
            score=model.score,
            accuracy=model.accuracy,
            max_combo=model.max_combo,
            cool=model.cool,
            good=model.good,
            bad=model.bad,
            miss=model.miss,
            created_at=model.created_at,
        )


# 사람마다 최고 기록 한 줄 — 같은 점수가 여러 번이면 가장 먼저 달성한 것
_BEST_PER_USER = """
    SELECT DISTINCT ON (p.user_id)
        p.user_id, p.score, p.accuracy, p.max_combo, p.created_at AS achieved_at
    FROM rhythm_plays p
    WHERE p.challenge_id = :challenge_id
      AND p.keys = :keys
      AND p.difficulty = :difficulty
      AND p.user_id IS NOT NULL
    ORDER BY p.user_id, p.score DESC, p.created_at ASC
"""

_RANKING = text(
    f"""
    WITH best AS ({_BEST_PER_USER})
    SELECT RANK() OVER (ORDER BY b.score DESC) AS rank,
           u.nickname, b.score, b.accuracy, b.max_combo, b.achieved_at
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


class RhythmRankingPgQuery(RhythmRankingQueryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ranking(
        self, challenge_id: int, keys: int, difficulty: RhythmDifficulty, limit: int
    ) -> list[RhythmRankingEntry]:
        rows = await self._session.execute(
            _RANKING,
            {
                "challenge_id": challenge_id,
                "keys": keys,
                "difficulty": difficulty.value,
                "limit": limit,
            },
        )
        return [
            RhythmRankingEntry(
                rank=int(r.rank),
                nickname=r.nickname,
                score=int(r.score),
                accuracy=float(r.accuracy),
                max_combo=int(r.max_combo),
                achieved_at=r.achieved_at,
            )
            for r in rows
        ]

    async def my_standing(
        self, challenge_id: int, keys: int, difficulty: RhythmDifficulty, user_id: int
    ) -> RhythmStanding | None:
        row = (
            await self._session.execute(
                _MY_STANDING,
                {
                    "challenge_id": challenge_id,
                    "keys": keys,
                    "difficulty": difficulty.value,
                    "user_id": user_id,
                },
            )
        ).first()
        if row is None:
            return None
        return RhythmStanding(rank=int(row.rank), best_score=int(row.best_score))
