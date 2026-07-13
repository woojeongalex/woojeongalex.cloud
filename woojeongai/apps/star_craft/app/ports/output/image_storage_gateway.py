from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStorageGateway(ABC):

    @abstractmethod
    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        """이미지를 저장하고 접근 가능한 URL을 반환한다."""
        pass
