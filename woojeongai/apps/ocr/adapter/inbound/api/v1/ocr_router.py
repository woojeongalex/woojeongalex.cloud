from fastapi import APIRouter, Depends, File, UploadFile

from ocr.adapter.inbound.api.schemas.ocr_schema import OcrResponse
from ocr.app.dtos.ocr_dto import OcrCommand
from ocr.app.ports.input.ocr_use_case import OcrUseCase
from ocr.dependencies.ocr_provider import get_ocr_use_case

ocr_router = APIRouter(prefix="/ocr", tags=["ocr"])


@ocr_router.post("/upload", summary="이미지를 올리고 글자를 읽어 낸다")
async def upload_and_extract(
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
