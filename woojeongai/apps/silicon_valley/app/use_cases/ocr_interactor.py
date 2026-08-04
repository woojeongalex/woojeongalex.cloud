from __future__ import annotations

from silicon_valley.app.dtos.ocr_dto import OcrCommand, OcrResult
from silicon_valley.app.ports.input.ocr_use_case import OcrUseCase
from silicon_valley.app.ports.output.ocr_port import OcrPort
from silicon_valley.app.ports.output.s3_image_storage_port import S3ImageStoragePort


class OcrInteractor(OcrUseCase):
    def __init__(self, storage: S3ImageStoragePort, ocr: OcrPort, bucket: str) -> None:
        self._storage = storage
        self._ocr = ocr
        self._bucket = bucket

    async def upload_and_extract(self, command: OcrCommand) -> OcrResult:
        url, key = await self._storage.upload(
            command.filename, command.content_type, command.data
        )
        text = await self._ocr.extract(self._bucket, key)
        return OcrResult(url=url, key=key, text=text)
