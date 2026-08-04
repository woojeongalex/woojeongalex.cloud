from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.ocr_dto import OcrCommand, OcrResult


class OcrUseCase(ABC):
    @abstractmethod
    async def upload_and_extract(self, command: OcrCommand) -> OcrResult:
        pass
