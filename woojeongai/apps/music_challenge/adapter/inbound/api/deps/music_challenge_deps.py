from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from music_challenge.app.ports.input.challenge_use_case import (
    CreateChallengeUseCase,
    GetChallengeUseCase,
    ListChallengesUseCase,
)
from music_challenge.app.ports.input.history_use_case import GetMyHistoryUseCase
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.dependencies.music_challenge_director import (
    get_challenge_use_case as _get,
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
