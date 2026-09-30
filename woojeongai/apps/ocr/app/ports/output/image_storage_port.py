from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStoragePort(ABC):
    """오브젝트 스토리지 구현은 adapter/outbound 만 안다."""

    @abstractmethod
    async def upload(
        self, filename: str, content_type: str, data: bytes
    ) -> tuple[str, str]:
        """이미지를 저장하고 (접근 URL, 저장 키)를 반환한다."""
