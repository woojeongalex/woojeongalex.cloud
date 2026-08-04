from fastapi import Depends

from core.matrix.aws_s3_manager import get_s3_manager
from silicon_valley.adapter.outbound.ocr.tesseract_adapter import TesseractOcrAdapter
from silicon_valley.adapter.outbound.s3.s3_image_storage_adapter import (
    S3ImageStorageAdapter,
)
from silicon_valley.app.ports.input.ocr_use_case import OcrUseCase
from silicon_valley.app.ports.output.ocr_port import OcrPort
from silicon_valley.app.ports.output.s3_image_storage_port import S3ImageStoragePort
from silicon_valley.app.use_cases.ocr_interactor import OcrInteractor


def get_ocr_storage_port() -> S3ImageStoragePort:
    return S3ImageStorageAdapter(s3_manager=get_s3_manager(), prefix="ocr")


def get_ocr_port() -> OcrPort:
    return TesseractOcrAdapter()


def get_ocr_use_case(
    storage: S3ImageStoragePort = Depends(get_ocr_storage_port),
    ocr: OcrPort = Depends(get_ocr_port),
) -> OcrUseCase:
    return OcrInteractor(storage=storage, ocr=ocr)
