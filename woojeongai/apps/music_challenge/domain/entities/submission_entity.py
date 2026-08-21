from dataclasses import dataclass
from datetime import datetime

from music_challenge.domain.value_objects.music_challenge_vo import MediaType


@dataclass(frozen=True)
class ChallengeSubmission:
    id: int
    challenge_id: int
    media_type: MediaType
    s3_key: str
    created_at: datetime
