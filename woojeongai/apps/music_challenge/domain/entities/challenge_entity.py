from dataclasses import dataclass
from datetime import datetime

from music_challenge.domain.value_objects.music_challenge_vo import ChallengeType


@dataclass(frozen=True)
class MusicChallenge:
    id: int
    title: str
    description: str
    music_s3_key: str
    challenge_type: ChallengeType
    is_active: bool
    created_at: datetime
