from dataclasses import dataclass

from music_challenge.domain.value_objects.music_challenge_vo import MediaType


@dataclass(frozen=True)
class SubmitChallengeCommand:
    challenge_id: int
    media_type: MediaType
    filename: str
    content_type: str
    data: bytes
    # 검증된 JWT 의 sub. 비로그인이면 None.
    username: str | None = None
    # 노래방·연주 모드 제출만. 녹음이 곡의 몇 초 지점부터 시작됐는지(기기 지연 반영).
    # 서버가 이 값으로 녹음을 정답 음표에 맞춰 다시 채점한다.
    karaoke_start_offset: float | None = None
