from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.s3_image_upload_dto import (
    S3ImageUploadCommand,
    S3ImageUploadResult,
)


class S3ImageUploadUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/s3_image_upload_router.py 와 대응."""

    @abstractmethod
    async def upload(self, command: S3ImageUploadCommand) -> S3ImageUploadResult:
        """업로드된 이미지를 S3에 저장하고 결과(URL·키)를 반환한다."""
        pass
