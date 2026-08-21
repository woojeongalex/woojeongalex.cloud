from dataclasses import dataclass

from music_challenge.domain.value_objects.music_challenge_vo import MediaType


@dataclass(frozen=True)
class SubmitChallengeCommand:
    challenge_id: int
    media_type: MediaType
    filename: str
    content_type: str
    data: bytes
