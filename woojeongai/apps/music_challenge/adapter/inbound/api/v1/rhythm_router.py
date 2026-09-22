"""리듬 게임(오투잼식) — 채보 조회·생성, 플레이 제출, 채보별 랭킹."""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from friday13th.adapter.inbound.api.deps.current_user_deps import (
    get_optional_user,
    require_admin,
)
from music_challenge.adapter.inbound.api.deps.music_challenge_deps import (
    get_list_rhythm_songs_use_case,
    get_request_rhythm_build_use_case,
    get_rhythm_chart_use_case,
    get_rhythm_ranking_use_case,
    get_submit_rhythm_play_use_case,
    run_build_rhythm_chart,
)
from music_challenge.adapter.inbound.api.schemas.rhythm_schema import (
    RhythmChartResponse,
    RhythmPlayRequest,
    RhythmPlayResponse,
    RhythmRankingEntryResponse,
    RhythmRankingResponse,
    RhythmSheetResponse,
    RhythmSheetSummaryResponse,
    RhythmSongListResponse,
    RhythmSongResponse,
    RhythmStandingResponse,
)
from music_challenge.app.dtos.rhythm_dto import (
    RhythmChartResult,
    SubmitRhythmPlayCommand,
)
from music_challenge.app.ports.input.rhythm_use_case import (
    GetRhythmChartUseCase,
    GetRhythmRankingUseCase,
    ListRhythmSongsUseCase,
    RequestRhythmBuildUseCase,
    SubmitRhythmPlayUseCase,
)
from music_challenge.domain.services.rhythm_scoring import Press
from music_challenge.domain.value_objects.rhythm_vo import RhythmDifficulty

rhythm_router = APIRouter(prefix="/challenges", tags=["music-challenge"])


def _chart_response(result: RhythmChartResult) -> RhythmChartResponse:
    return RhythmChartResponse(
        challenge_id=result.challenge_id,
        status=result.status.value,
        bpm=result.bpm,
        duration=result.duration,
        audio_url=result.audio_url,
        sheets=[
            RhythmSheetSummaryResponse(
                keys=s.keys,
                difficulty=s.difficulty,
                level=s.level,
                note_count=s.note_count,
            )
            for s in result.sheets
        ],
        error=result.error,
    )


@rhythm_router.get("/{challenge_id}/rhythm", response_model=RhythmChartResponse)
async def get_rhythm_chart(
    challenge_id: int,
    use_case: GetRhythmChartUseCase = Depends(get_rhythm_chart_use_case),
) -> RhythmChartResponse:
    return _chart_response(await use_case.get(challenge_id))


@rhythm_router.post(
    "/{challenge_id}/rhythm/build",
    response_model=RhythmChartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def build_rhythm_chart(
    challenge_id: int,
    background: BackgroundTasks,
    _admin: dict = Depends(require_admin),
    use_case: RequestRhythmBuildUseCase = Depends(get_request_rhythm_build_use_case),
) -> RhythmChartResponse:
    """원곡으로 채보 6개(4키·7키 × 3난이도)를 만든다.

    분석에 10~20초가 걸려 응답 뒤에 돌린다. 화면은 GET /rhythm 의 status 로 확인한다.
    """
    result, job_id, source_key = await use_case.request(challenge_id)
    background.add_task(run_build_rhythm_chart, challenge_id, job_id, source_key)
    return _chart_response(result)


@rhythm_router.get(
    "/{challenge_id}/rhythm/{keys}/{difficulty}", response_model=RhythmSheetResponse
)
async def get_rhythm_sheet(
    challenge_id: int,
    keys: int,
    difficulty: RhythmDifficulty,
    use_case: GetRhythmChartUseCase = Depends(get_rhythm_chart_use_case),
) -> RhythmSheetResponse:
    sheet = await use_case.get_sheet(challenge_id, keys, difficulty)
    return RhythmSheetResponse(
        challenge_id=sheet.challenge_id,
        keys=sheet.keys,
        difficulty=sheet.difficulty,
        level=sheet.level,
        bpm=sheet.bpm,
        duration=sheet.duration,
        audio_url=sheet.audio_url,
        notes=[(n.time, n.lane, n.end) for n in sheet.notes],
    )


@rhythm_router.post(
    "/{challenge_id}/rhythm/{keys}/{difficulty}/plays",
    response_model=RhythmPlayResponse,
)
async def submit_rhythm_play(
    challenge_id: int,
    keys: int,
    difficulty: RhythmDifficulty,
    body: RhythmPlayRequest,
    use_case: SubmitRhythmPlayUseCase = Depends(get_submit_rhythm_play_use_case),
    user: dict | None = Depends(get_optional_user),
) -> RhythmPlayResponse:
    """입력 기록을 받아 서버가 다시 채점한다. 로그인했을 때만 랭킹에 오른다."""
    result = await use_case.submit(
        SubmitRhythmPlayCommand(
            challenge_id=challenge_id,
            keys=keys,
            difficulty=difficulty,
            presses=[Press(lane=lane, down=d, up=u) for lane, d, u in body.presses],
            username=user.get("sub") if user else None,
        )
    )
    return RhythmPlayResponse(
        score=result.score,
        accuracy=result.accuracy,
        max_combo=result.max_combo,
        cool=result.cool,
        good=result.good,
        bad=result.bad,
        miss=result.miss,
        rank=result.rank,
        best_score=result.best_score,
        is_personal_best=result.is_personal_best,
    )


@rhythm_router.get(
    "/{challenge_id}/rhythm/{keys}/{difficulty}/ranking",
    response_model=RhythmRankingResponse,
)
async def rhythm_ranking(
    challenge_id: int,
    keys: int,
    difficulty: RhythmDifficulty,
    limit: int = Query(20, ge=1, le=100),
    use_case: GetRhythmRankingUseCase = Depends(get_rhythm_ranking_use_case),
    user: dict | None = Depends(get_optional_user),
) -> RhythmRankingResponse:
    entries, me = await use_case.get(
        challenge_id, keys, difficulty, limit, user.get("sub") if user else None
    )
    return RhythmRankingResponse(
        items=[
            RhythmRankingEntryResponse(
                rank=e.rank,
                nickname=e.nickname,
                score=e.score,
                accuracy=e.accuracy,
                max_combo=e.max_combo,
                achieved_at=e.achieved_at,
            )
            for e in entries
        ],
        me=RhythmStandingResponse(rank=me.rank, best_score=me.best_score)
        if me
        else None,
    )


# 리듬 게임은 챌린지와 별도 메뉴라 곡 목록은 /rhythm 아래에 둔다.
rhythm_songs_router = APIRouter(prefix="/rhythm", tags=["music-challenge"])


@rhythm_songs_router.get("/songs", response_model=RhythmSongListResponse)
async def list_rhythm_songs(
    use_case: ListRhythmSongsUseCase = Depends(get_list_rhythm_songs_use_case),
) -> RhythmSongListResponse:
    """채보가 준비된 곡 목록. 누구나 볼 수 있다."""
    return RhythmSongListResponse(
        items=[
            RhythmSongResponse(
                challenge_id=s.challenge_id,
                title=s.title,
                bpm=s.bpm,
                duration=s.duration,
                sheets=[
                    RhythmSheetSummaryResponse(
                        keys=x.keys,
                        difficulty=x.difficulty,
                        level=x.level,
                        note_count=x.note_count,
                    )
                    for x in s.sheets
                ],
            )
            for s in await use_case.list()
        ]
    )
