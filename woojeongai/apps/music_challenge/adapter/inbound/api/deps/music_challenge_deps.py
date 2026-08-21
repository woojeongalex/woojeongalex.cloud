from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.app.ports.input.challenge_use_case import (
    CreateChallengeUseCase,
    GetChallengeUseCase,
    ListChallengesUseCase,
)
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.dependencies.music_challenge_director import (
    get_create_challenge_use_case as _create,
    get_challenge_use_case as _get,
    get_list_challenges_use_case as _list,
    get_submit_challenge_use_case as _submit,
)

from database import get_db


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
