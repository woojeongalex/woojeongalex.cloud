from music_challenge.adapter.inbound.api.schemas.challenge_schema import (
    ChallengeResponse,
)
from music_challenge.app.dtos.challenge_dto import ChallengeResult


def challenge_result_to_response(result: ChallengeResult) -> ChallengeResponse:
    return ChallengeResponse(
        id=result.id,
        title=result.title,
        description=result.description,
        music_url=result.music_url,
        challenge_type=result.challenge_type.value,
        is_active=result.is_active,
    )
