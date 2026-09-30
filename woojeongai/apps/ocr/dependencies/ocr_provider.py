from fastapi import Depends

from core.matrix.aws_s3_manager import get_s3_manager
from ocr.adapter.outbound.s3_image_storage_adapter import S3ImageStorageAdapter
from ocr.adapter.outbound.tesseract_ocr_adapter import TesseractOcrAdapter
from ocr.app.ports.input.ocr_use_case import OcrUseCase
from ocr.app.ports.output.image_storage_port import ImageStoragePort
from ocr.app.ports.output.ocr_port import OcrPort
from ocr.app.use_cases.ocr_interactor import OcrInteractor


def get_image_storage_port() -> ImageStoragePort:
    return S3ImageStorageAdapter(s3_manager=get_s3_manager(), prefix="ocr")


def get_ocr_port() -> OcrPort:
    return TesseractOcrAdapter()


def get_ocr_use_case(
    storage: ImageStoragePort = Depends(get_image_storage_port),
    ocr: OcrPort = Depends(get_ocr_port),
) -> OcrUseCase:
    return OcrInteractor(storage=storage, ocr=ocr)
