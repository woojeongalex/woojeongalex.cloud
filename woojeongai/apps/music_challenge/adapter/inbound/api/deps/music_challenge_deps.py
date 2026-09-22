from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from music_challenge.app.ports.input.challenge_use_case import (
    CreateChallengeUseCase,
    GetChallengeUseCase,
    ListChallengesUseCase,
)
from music_challenge.app.ports.input.chart_use_case import (
    GetChartUseCase,
    UpdateLyricsUseCase,
    UploadStemsUseCase,
)
from music_challenge.app.ports.input.history_use_case import GetMyHistoryUseCase
from music_challenge.app.ports.input.ranking_use_case import (
    GetChallengeRankingUseCase,
    GetWeeklyRankingUseCase,
)
from music_challenge.domain.value_objects.chart_vo import MelodySource
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.dependencies.music_challenge_director import (
    get_build_chart_use_case as _build_chart,
)
from music_challenge.dependencies.music_challenge_director import (
    get_challenge_ranking_use_case as _challenge_ranking,
)
from music_challenge.dependencies.music_challenge_director import (
    get_challenge_use_case as _get,
)
from music_challenge.dependencies.music_challenge_director import (
    get_chart_use_case as _chart,
)
from music_challenge.dependencies.music_challenge_director import (
    get_create_challenge_use_case as _create,
)
from music_challenge.dependencies.music_challenge_director import (
    get_list_challenges_use_case as _list,
)
from music_challenge.dependencies.music_challenge_director import (
    get_my_history_use_case as _history,
)
from music_challenge.dependencies.music_challenge_director import (
    get_submit_challenge_use_case as _submit,
)
from music_challenge.dependencies.music_challenge_director import (
    get_update_lyrics_use_case as _update_lyrics,
)
from music_challenge.dependencies.music_challenge_director import (
    get_upload_stems_use_case as _upload_stems,
)
from music_challenge.dependencies.music_challenge_director import (
    get_weekly_ranking_use_case as _weekly_ranking,
)


def get_create_challenge_use_case(
    session: AsyncSession = Depends(get_db),
) -> CreateChallengeUseCase:
    return _create(session)


def get_list_challenges_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListChallengesUseCase:
    return _list(session)


def get_challenge_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetChallengeUseCase:
    return _get(session)


def get_submit_challenge_use_case(
    session: AsyncSession = Depends(get_db),
) -> SubmitChallengeUseCase:
    return _submit(session)


def get_my_history_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetMyHistoryUseCase:
    return _history(session)


def get_chart_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetChartUseCase:
    return _chart(session)


def get_upload_stems_use_case(
    session: AsyncSession = Depends(get_db),
) -> UploadStemsUseCase:
    return _upload_stems(session)


def get_update_lyrics_use_case(
    session: AsyncSession = Depends(get_db),
) -> UpdateLyricsUseCase:
    return _update_lyrics(session)


async def run_build_chart(
    challenge_id: int, melody_key: str, melody_bytes: bytes, source: MelodySource
) -> None:
    """BackgroundTasks 용. 요청 세션은 응답과 함께 닫히므로 새 세션을 연다."""
    async for session in get_db():
        await _build_chart(session).build(
            challenge_id, melody_key, melody_bytes, source
        )


def get_challenge_ranking_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetChallengeRankingUseCase:
    return _challenge_ranking(session)


def get_weekly_ranking_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetWeeklyRankingUseCase:
    return _weekly_ranking(session)
