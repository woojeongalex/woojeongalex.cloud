from __future__ import annotations

from silicon_valley.app.dtos.s3_image_upload_dto import (
    S3ImageUploadCommand,
    S3ImageUploadResult,
)
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from silicon_valley.app.ports.output.s3_image_storage_port import S3ImageStoragePort


class S3ImageUploadInteractor(S3ImageUploadUseCase):
    def __init__(self, storage: S3ImageStoragePort):
        self.storage = storage

    async def upload(self, command: S3ImageUploadCommand) -> S3ImageUploadResult:
        url, key = await self.storage.upload(
            command.filename, command.content_type, command.data
        )
        return S3ImageUploadResult(url=url, key=key)
