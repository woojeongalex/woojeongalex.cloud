from abc import ABC, abstractmethod

from music_challenge.domain.value_objects.music_challenge_vo import ChallengeType, MediaType


class AIEvaluatorPort(ABC):
    @abstractmethod
    async def evaluate(
        self,
        challenge_title: str,
        challenge_description: str,
        challenge_type: ChallengeType,
        media_bytes: bytes,
        media_type: MediaType,
        content_type: str,
    ) -> tuple[int, str]: ...
