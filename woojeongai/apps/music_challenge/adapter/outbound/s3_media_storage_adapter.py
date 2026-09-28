import asyncio

from botocore.exceptions import ClientError

from core.matrix.aws_s3_manager import get_s3_manager
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.domain.services.playback_media import playback_key_for

# 재생용 MP3 가 있는지 물어본 결과. 키는 바뀌지 않으므로 한 번만 확인하면 된다.
_playback_cache: dict[str, str] = {}


class S3MediaStorageAdapter(MediaStoragePort):
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: get_s3_manager().put_bytes(key, data, content_type),
        )

    async def presigned_url(self, key: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: get_s3_manager().presigned_url(key),
        )

    async def playback_url(self, key: str) -> str:
        return await self.presigned_url(await self._playback_key(key))

    async def _playback_key(self, key: str) -> str:
        """MP3 가 실제로 있을 때만 그 키를 쓴다. 없으면 원본 그대로."""
        cached = _playback_cache.get(key)
        if cached is not None:
            return cached

        mp3 = playback_key_for(key)
        chosen = key
        if mp3:
            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, lambda: get_s3_manager().head(mp3))
                chosen = mp3
            except ClientError:
                chosen = key
        _playback_cache[key] = chosen
        return chosen

    async def download(self, key: str) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: get_s3_manager().get_bytes(key),
        )
