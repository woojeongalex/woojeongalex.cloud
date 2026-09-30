from __future__ import annotations

from abc import ABC, abstractmethod

from ocr.app.dtos.ocr_dto import OcrCommand, OcrResult


class OcrUseCase(ABC):
    @abstractmethod
    async def upload_and_extract(self, command: OcrCommand) -> OcrResult:
        """이미지를 보관하고 거기서 읽어 낸 글자를 함께 돌려준다."""
