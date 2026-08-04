from fastapi import APIRouter, Depends, File, UploadFile

from silicon_valley.adapter.inbound.api.schemas.s3_image_upload_schema import (
    S3ImageUploadResponse,
)
from silicon_valley.app.dtos.s3_image_upload_dto import S3ImageUploadCommand
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
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
