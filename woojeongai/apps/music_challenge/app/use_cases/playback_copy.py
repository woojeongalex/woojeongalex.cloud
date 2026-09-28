"""올라온 음원의 재생용 사본 만들기.

원본은 분석(박자·음정 추출)에 쓰고, 브라우저에는 MP3 를 준다. 곡 등록과 스템 업로드
두 곳에서 같은 일을 해서 여기로 모았다.

재생 쪽은 `MediaStoragePort.playback_url` 이 같은 자리의 `.mp3` 를 찾아 쓴다.
그래서 키를 DB 에 따로 저장하지 않아도 되고, 변환이 실패한 곡은 원본으로 재생된다.
"""

import logging

from music_challenge.app.ports.output.audio_transcoder_port import AudioTranscoderPort
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.domain.services.playback_media import playback_key_for

logger = logging.getLogger(__name__)


async def store_playback_copy(
    storage: MediaStoragePort,
    transcoder: AudioTranscoderPort,
    key: str,
    data: bytes,
) -> None:
    """원본 옆에 재생용 MP3 를 둔다. 실패해도 곡 등록은 그대로 살린다."""
    mp3_key = playback_key_for(key)
    if not mp3_key:
        return
    mp3 = await transcoder.to_mp3(data)
    if mp3 is None:
        logger.info("재생용 MP3 를 만들지 못해 원본으로 재생합니다: %s", key)
        return
    await storage.upload(mp3_key, mp3, "audio/mpeg")
    logger.info(
        "재생용 MP3 저장: %s (%.1fMB → %.1fMB)",
        mp3_key,
        len(data) / 1048576,
        len(mp3) / 1048576,
    )
