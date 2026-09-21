import uuid
from datetime import datetime

from music_challenge.app.dtos.challenge_dto import (
    ChallengeResult,
    CreateChallengeCommand,
)
from music_challenge.app.ports.input.challenge_use_case import CreateChallengeUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.domain.entities.challenge_entity import MusicChallenge


class CreateChallengeInteractor(CreateChallengeUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._storage = storage

    async def create(self, command: CreateChallengeCommand) -> ChallengeResult:
        key = f"music_challenge/music/{uuid.uuid4()}_{command.filename}"
        await self._storage.upload(key, command.data, command.content_type)

        challenge = MusicChallenge(
            id=0,
            title=command.title,
            description=command.description,
            music_s3_key=key,
            challenge_type=command.challenge_type,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        saved = await self._challenge_repo.save(challenge)
        music_url = await self._storage.presigned_url(saved.music_s3_key)

        return ChallengeResult(
            id=saved.id,
            title=saved.title,
            description=saved.description,
            music_url=music_url,
            challenge_type=saved.challenge_type,
            is_active=saved.is_active,
        )
