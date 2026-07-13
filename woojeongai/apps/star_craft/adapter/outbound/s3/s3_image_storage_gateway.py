from __future__ import annotations

import asyncio
import logging
import uuid

import boto3

from star_craft.app.ports.output.image_storage_gateway import ImageStorageGateway

logger = logging.getLogger(__name__)


class S3ImageStorageGateway(ImageStorageGateway):
    """AWS S3 버킷에 이미지를 저장하는 게이트웨이."""

    def __init__(self, bucket: str, region: str, prefix: str = "vision") -> None:
        self._bucket = bucket
        self._prefix = prefix
        self._client = boto3.client("s3", region_name=region)

    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        return await asyncio.to_thread(self._save_sync, filename, content_type, data)

    def _save_sync(self, filename: str, content_type: str, data: bytes) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        key = f"{self._prefix}/{uuid.uuid4().hex}.{ext}"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        logger.info("[S3ImageStorageGateway] 업로드 완료 → s3://%s/%s", self._bucket, key)
        return f"https://{self._bucket}.s3.{self._client.meta.region_name}.amazonaws.com/{key}"
