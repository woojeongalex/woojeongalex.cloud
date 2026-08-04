from __future__ import annotations

import asyncio
import uuid

from core.matrix.aws_s3_manager import S3Manager
from silicon_valley.app.ports.output.s3_image_storage_port import S3ImageStoragePort


class S3ImageStorageAdapter(S3ImageStoragePort):
    """S3Manager(Keymaker 자격 증명, AWS_S3_BUCKET)를 통해 이미지를 저장하는 어댑터."""

    def __init__(self, s3_manager: S3Manager, prefix: str = "silicon_valley"):
        self._s3 = s3_manager
        self._prefix = prefix

    async def upload(
        self, filename: str, content_type: str, data: bytes
    ) -> tuple[str, str]:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        key = f"{self._prefix}/{uuid.uuid4().hex}.{ext}"
        await asyncio.to_thread(self._s3.put_bytes, key, data, content_type)
        # 버킷이 비공개라 put_bytes가 돌려주는 원본 주소는 브라우저에서 403이 난다.
        url = await asyncio.to_thread(self._s3.presigned_url, key)
        return url, key
