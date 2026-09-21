from fastapi import APIRouter, Depends, File, Form, UploadFile

from music_challenge.adapter.inbound.api.deps.music_challenge_deps import (
    get_challenge_use_case,
    get_create_challenge_use_case,
    get_list_challenges_use_case,
)
from music_challenge.adapter.inbound.api.mappers.challenge_mapper import (
    challenge_result_to_response,
)
from music_challenge.adapter.inbound.api.schemas.challenge_schema import (
    ChallengeResponse,
    ChallengesListResponse,
)
from music_challenge.app.dtos.challenge_dto import CreateChallengeCommand
from music_challenge.app.ports.input.challenge_use_case import (
    CreateChallengeUseCase,
    GetChallengeUseCase,
    ListChallengesUseCase,
)
from music_challenge.domain.value_objects.music_challenge_vo import ChallengeType

challenges_router = APIRouter(prefix="/challenges", tags=["music-challenge"])


@challenges_router.get("", response_model=ChallengesListResponse)
async def list_challenges(
    use_case: ListChallengesUseCase = Depends(get_list_challenges_use_case),
) -> ChallengesListResponse:
    results = await use_case.list_active()
    items = [challenge_result_to_response(r) for r in results]
    return ChallengesListResponse(items=items, total=len(items))


@challenges_router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: int,
    use_case: GetChallengeUseCase = Depends(get_challenge_use_case),
) -> ChallengeResponse:
    result = await use_case.get(challenge_id)
    return challenge_result_to_response(result)


@challenges_router.post("", response_model=ChallengeResponse)
async def create_challenge(
    title: str = Form(...),
    description: str = Form(...),
    challenge_type: ChallengeType = Form(...),
    music_file: UploadFile = File(...),
    use_case: CreateChallengeUseCase = Depends(get_create_challenge_use_case),
) -> ChallengeResponse:
    data = await music_file.read()
    result = await use_case.create(
        CreateChallengeCommand(
            title=title,
            description=description,
            challenge_type=challenge_type,
            filename=music_file.filename or "music",
            content_type=music_file.content_type or "audio/mpeg",
            data=data,
        )
    )
    return challenge_result_to_response(result)
