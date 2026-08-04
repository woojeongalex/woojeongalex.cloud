from __future__ import annotations

from abc import ABC, abstractmethod


class OcrPort(ABC):
    @abstractmethod
    async def extract(self, bucket: str, key: str) -> str:
        """S3에 저장된 이미지에서 텍스트를 추출한다."""
        pass
