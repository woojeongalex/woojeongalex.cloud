import asyncio

from core.matrix.aws_s3_manager import get_s3_manager
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort


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
