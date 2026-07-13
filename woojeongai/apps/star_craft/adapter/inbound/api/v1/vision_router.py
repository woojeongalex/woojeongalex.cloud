import asyncio

from fastapi import APIRouter, Depends, File, UploadFile

from star_craft.adapter.inbound.api.schemas.vision_schema import VisionSchema
from star_craft.adapter.inbound.api.schemas.yolo_schema import (
    YoloPredictResponse,
    YoloTrainRequest,
    YoloTrainResponse,
)
from star_craft.app.dtos.vision_dto import VisionImageQuery, VisionImageResponse, VisionResponse
from star_craft.app.dtos.yolo_dto import YoloPredictCommand, YoloTrainCommand
from star_craft.app.ports.input.vision_use_case import VisionUseCase
from star_craft.app.ports.input.yolo_use_case import YoloUseCase
from star_craft.dependencies.vision_provider import get_vision_use_case
from star_craft.dependencies.yolo_provider import get_yolo_use_case

vision_router = APIRouter(prefix="/vision", tags=["vision"])

@vision_router.get("/myself")
async def introduce_myself(
    vision: VisionUseCase = Depends(get_vision_use_case)
) -> VisionResponse:
    return await vision.introduce_myself(
        VisionSchema(id=1, name="Vision")
    )


@vision_router.post("/upload", summary="비전 처리용 이미지 업로드")
async def upload_image(
    file: UploadFile = File(...),
    vision: VisionUseCase = Depends(get_vision_use_case),
) -> VisionImageResponse:
    content = await file.read()
    return await vision.process_image(
        VisionImageQuery(
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            data=content,
        )
    )


@vision_router.post(
    "/yolo-train",
    response_model=YoloTrainResponse,
    summary="사람 얼굴 인식 YOLO 분류 모델 파인튜닝",
)
async def train_yolo(
    body: YoloTrainRequest,
    use_case: YoloUseCase = Depends(get_yolo_use_case),
) -> YoloTrainResponse:
    command = YoloTrainCommand(
        epochs=body.epochs,
        batch_size=body.batch_size,
        imgsz=body.imgsz,
        device=body.device,
    )
    # 학습은 CPU/GPU-bound 장시간 작업이므로 이벤트 루프를 막지 않도록 스레드로 위임한다.
    result = await asyncio.to_thread(use_case.execute, command)
    return YoloTrainResponse(
        dataset_root=result.dataset_root,
        epochs=result.epochs,
        classes=result.classes,
        weights_path=result.weights_path,
    )


@vision_router.post(
    "/yolo-predict",
    response_model=YoloPredictResponse,
    summary="업로드된 얼굴 이미지로 인물 예측",
)
async def predict_yolo(
    file: UploadFile = File(...),
    use_case: YoloUseCase = Depends(get_yolo_use_case),
) -> YoloPredictResponse:
    content = await file.read()
    command = YoloPredictCommand(image=content, device="cpu")
    result = await asyncio.to_thread(use_case.predict, command)
    return YoloPredictResponse(name=result.name, confidence=result.confidence)
