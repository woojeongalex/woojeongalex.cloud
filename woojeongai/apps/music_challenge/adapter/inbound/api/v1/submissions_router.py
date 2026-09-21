from fastapi import APIRouter, Depends, File, Form, UploadFile

from friday13th.adapter.inbound.api.deps.current_user_deps import get_optional_user
from music_challenge.adapter.inbound.api.deps.music_challenge_deps import (
    get_submit_challenge_use_case,
)
from music_challenge.adapter.inbound.api.mappers.submission_mapper import (
    evaluation_result_to_response,
)
from music_challenge.adapter.inbound.api.schemas.submission_schema import (
    EvaluationResponse,
)
from music_challenge.app.dtos.submission_dto import SubmitChallengeCommand
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.domain.value_objects.music_challenge_vo import MediaType

submissions_router = APIRouter(prefix="/submissions", tags=["music-challenge"])


@submissions_router.post("/submit", response_model=EvaluationResponse)
async def submit_challenge(
    challenge_id: int = Form(...),
    media_type: MediaType = Form(...),
    media_file: UploadFile = File(...),
    use_case: SubmitChallengeUseCase = Depends(get_submit_challenge_use_case),
    user: dict | None = Depends(get_optional_user),
) -> EvaluationResponse:
    data = await media_file.read()
    result = await use_case.submit(
        SubmitChallengeCommand(
            challenge_id=challenge_id,
            media_type=media_type,
            filename=media_file.filename or "submission",
            content_type=media_file.content_type or "audio/mpeg",
            data=data,
            # 로그인 상태면 토큰의 sub(username). 비로그인이면 None.
            username=user.get("sub") if user else None,
        )
    )
    return evaluation_result_to_response(result)
