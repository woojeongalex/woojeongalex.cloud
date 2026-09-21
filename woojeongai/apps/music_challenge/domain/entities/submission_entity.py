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
    # 비로그인 제출은 None. 서버가 JWT 에서 도출한 값만 채운다.
    user_id: int | None = None
