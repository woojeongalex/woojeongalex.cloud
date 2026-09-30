from __future__ import annotations

from abc import ABC, abstractmethod


class OcrPort(ABC):
    @abstractmethod
    async def extract(self, data: bytes) -> str:
        """이미지 바이트에서 텍스트를 추출한다."""
