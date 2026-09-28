from music_challenge.app.dtos.challenge_dto import ChallengeResult
from music_challenge.app.ports.input.challenge_use_case import ListChallengesUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort


class ListChallengesInteractor(ListChallengesUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._storage = storage

    async def list_active(self) -> list[ChallengeResult]:
        challenges = await self._challenge_repo.find_all_active()
        results = []
        for c in challenges:
            music_url = await self._storage.playback_url(c.music_s3_key)
            results.append(
                ChallengeResult(
                    id=c.id,
                    title=c.title,
                    description=c.description,
                    music_url=music_url,
                    challenge_type=c.challenge_type,
                    is_active=c.is_active,
                )
            )
        return results
