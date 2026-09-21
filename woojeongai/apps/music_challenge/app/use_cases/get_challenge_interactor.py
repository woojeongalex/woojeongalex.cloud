from fastapi import HTTPException

from music_challenge.app.dtos.challenge_dto import ChallengeResult
from music_challenge.app.ports.input.challenge_use_case import GetChallengeUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort


class GetChallengeInteractor(GetChallengeUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._storage = storage

    async def get(self, challenge_id: int) -> ChallengeResult:
        challenge = await self._challenge_repo.find_by_id(challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        music_url = await self._storage.presigned_url(challenge.music_s3_key)
        return ChallengeResult(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            music_url=music_url,
            challenge_type=challenge.challenge_type,
            is_active=challenge.is_active,
        )
