from __future__ import annotations

from abc import ABC, abstractmethod


class S3ImageStoragePort(ABC):
    """Outbound 포트 — S3 등 오브젝트 스토리지 구현은 adapter/outbound에서만 안다."""

    @abstractmethod
    async def upload(
        self, filename: str, content_type: str, data: bytes
    ) -> tuple[str, str]:
        """이미지를 저장하고 (접근 URL, 저장 키)를 반환한다."""
        pass
