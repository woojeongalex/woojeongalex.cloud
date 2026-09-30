from __future__ import annotations

import asyncio

from ocr.app.dtos.ocr_dto import OcrCommand, OcrResult
from ocr.app.ports.input.ocr_use_case import OcrUseCase
from ocr.app.ports.output.image_storage_port import ImageStoragePort
from ocr.app.ports.output.ocr_port import OcrPort


class OcrInteractor(OcrUseCase):
    def __init__(self, storage: ImageStoragePort, ocr: OcrPort) -> None:
        self._storage = storage
        self._ocr = ocr

    async def upload_and_extract(self, command: OcrCommand) -> OcrResult:
        # 적재(네트워크 I/O)와 인식(CPU)은 서로를 기다릴 이유가 없다.
        (url, key), text = await asyncio.gather(
            self._storage.upload(command.filename, command.content_type, command.data),
            self._ocr.extract(command.data),
        )
        return OcrResult(url=url, key=key, text=text)
