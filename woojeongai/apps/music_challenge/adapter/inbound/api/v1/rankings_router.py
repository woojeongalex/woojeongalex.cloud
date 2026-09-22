"""노래방·연주 랭킹 — 곡별, 이번 주 전체."""

from fastapi import APIRouter, Depends, Query

from friday13th.adapter.inbound.api.deps.current_user_deps import get_optional_user
from music_challenge.adapter.inbound.api.deps.music_challenge_deps import (
    get_challenge_ranking_use_case,
    get_weekly_ranking_use_case,
)
from music_challenge.adapter.inbound.api.schemas.ranking_schema import (
    ChallengeRankingResponse,
    MyStandingResponse,
    RankingEntryResponse,
    WeeklyRankingEntryResponse,
    WeeklyRankingResponse,
)
from music_challenge.app.ports.input.ranking_use_case import (
    GetChallengeRankingUseCase,
    GetWeeklyRankingUseCase,
)

rankings_router = APIRouter(tags=["music-challenge"])


@rankings_router.get(
    "/challenges/{challenge_id}/ranking", response_model=ChallengeRankingResponse
)
async def challenge_ranking(
    challenge_id: int,
    limit: int = Query(20, ge=1, le=100),
    use_case: GetChallengeRankingUseCase = Depends(get_challenge_ranking_use_case),
    user: dict | None = Depends(get_optional_user),
) -> ChallengeRankingResponse:
    """누구나 볼 수 있다. 로그인했으면 내 순위를 함께 준다."""
    entries, me = await use_case.get(
        challenge_id, limit, user.get("sub") if user else None
    )
    return ChallengeRankingResponse(
        items=[
            RankingEntryResponse(
                rank=e.rank,
                nickname=e.nickname,
                score=e.score,
                pitch_accuracy=e.pitch_accuracy,
                timing_accuracy=e.timing_accuracy,
                achieved_at=e.achieved_at,
            )
            for e in entries
        ],
        me=MyStandingResponse(rank=me.rank, best_score=me.best_score) if me else None,
    )


@rankings_router.get("/rankings/weekly", response_model=WeeklyRankingResponse)
async def weekly_ranking(
    limit: int = Query(10, ge=1, le=50),
    use_case: GetWeeklyRankingUseCase = Depends(get_weekly_ranking_use_case),
) -> WeeklyRankingResponse:
    """이번 주(한국 시간 월요일 0시부터) 사람마다 가장 높은 기록 한 곡."""
    entries = await use_case.get(limit)
    return WeeklyRankingResponse(
        items=[
            WeeklyRankingEntryResponse(
                rank=e.rank,
                nickname=e.nickname,
                score=e.score,
                pitch_accuracy=e.pitch_accuracy,
                timing_accuracy=e.timing_accuracy,
                achieved_at=e.achieved_at,
                challenge_id=e.challenge_id,
                challenge_title=e.challenge_title,
            )
            for e in entries
        ]
    )
