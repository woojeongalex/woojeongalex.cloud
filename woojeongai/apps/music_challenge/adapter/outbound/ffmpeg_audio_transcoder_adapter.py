"""ffmpeg 으로 재생용 MP3 를 만든다.

ffmpeg 은 파이프로 wav 를 받아 mp3 를 뱉을 수 있어 임시 파일을 만들지 않는다.
192kbps 는 반주·게임용으로 원본과 구분하기 어려운 수준이면서 8배쯤 작다.
"""

import asyncio
import logging

from music_challenge.app.ports.output.audio_transcoder_port import AudioTranscoderPort

logger = logging.getLogger(__name__)

_BITRATE = "192k"
# 40MB 짜리 곡도 EC2(코어 2개, 메모리 912MB)에서 이 안에는 끝난다.
_TIMEOUT_SEC = 180


class FfmpegAudioTranscoderAdapter(AudioTranscoderPort):
    async def to_mp3(self, data: bytes) -> bytes | None:
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-nostdin",
                "-loglevel",
                "error",
                "-i",
                "pipe:0",
                "-codec:a",
                "libmp3lame",
                "-b:a",
                _BITRATE,
                "-f",
                "mp3",
                "pipe:1",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            logger.warning("ffmpeg 이 없어 재생용 MP3 를 만들지 못했습니다")
            return None

        try:
            out, err = await asyncio.wait_for(
                proc.communicate(data), timeout=_TIMEOUT_SEC
            )
        except TimeoutError:
            proc.kill()
            logger.warning("MP3 변환이 %d초를 넘겨 중단했습니다", _TIMEOUT_SEC)
            return None

        if proc.returncode != 0 or not out:
            logger.warning(
                "MP3 변환 실패 (코드 %s): %s",
                proc.returncode,
                err.decode("utf-8", "replace")[:200],
            )
            return None
        return out
