from dataclasses import dataclass

from music_challenge.domain.value_objects.music_challenge_vo import ChallengeType


@dataclass(frozen=True)
class CreateChallengeCommand:
    title: str
    description: str
    challenge_type: ChallengeType
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class ChallengeResult:
    id: int
    title: str
    description: str
    music_url: str
    challenge_type: ChallengeType
    is_active: bool
