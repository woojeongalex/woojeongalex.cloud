from fastapi import APIRouter, Depends, File, UploadFile

from silicon_valley.adapter.inbound.api.schemas.s3_image_upload_schema import (
    OcrResponse,
    S3ImageUploadResponse,
)
from silicon_valley.app.dtos.ocr_dto import OcrCommand
from silicon_valley.app.dtos.s3_image_upload_dto import S3ImageUploadCommand
from silicon_valley.app.ports.input.ocr_use_case import OcrUseCase
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from silicon_valley.dependencies.ocr_provider import get_ocr_use_case
from silicon_valley.dependencies.s3_image_upload_provider import (
    get_s3_image_upload_use_case,
)

s3_image_upload_router = APIRouter(prefix="/s3-image", tags=["s3-image-upload"])


@s3_image_upload_router.post("/upload", summary="이미지를 S3에 업로드")
async def upload_image(
    file: UploadFile = File(...),
    use_case: S3ImageUploadUseCase = Depends(get_s3_image_upload_use_case),
) -> S3ImageUploadResponse:
    data = await file.read()
    result = await use_case.upload(
        S3ImageUploadCommand(
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )
    )
    return S3ImageUploadResponse(url=result.url, key=result.key)


@s3_image_upload_router.post("/upload-ocr", summary="이미지 업로드 후 OCR 텍스트 추출")
async def upload_and_ocr(
    file: UploadFile = File(...),
    use_case: OcrUseCase = Depends(get_ocr_use_case),
) -> OcrResponse:
    data = await file.read()
    result = await use_case.upload_and_extract(
        OcrCommand(
            filename=file.filename or "unknown",
            content_type=file.content_type or "image/jpeg",
            data=data,
        )
    )
    return OcrResponse(url=result.url, key=result.key, text=result.text)
