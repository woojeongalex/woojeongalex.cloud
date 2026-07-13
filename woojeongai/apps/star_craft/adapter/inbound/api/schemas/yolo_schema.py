from pydantic import BaseModel, Field


class YoloTrainRequest(BaseModel):

    epochs: int = Field(50, description="학습 epoch 수")
    batch_size: int = Field(16, description="배치 크기")
    imgsz: int = Field(224, description="입력 이미지 크기")
    device: str = Field("mps", description="학습 디바이스 (mps/cpu/0 등)")


class YoloTrainResponse(BaseModel):

    dataset_root: str = Field(..., description="학습에 사용된 데이터셋 루트 경로")
    epochs: int = Field(..., description="학습한 epoch 수")
    classes: list[str] = Field(..., description="인식 대상 인물(클래스) 목록")
    weights_path: str = Field(..., description="학습된 가중치(best.pt) 경로")


class YoloPredictResponse(BaseModel):

    name: str = Field(..., description="예측된 인물 이름")
    confidence: float = Field(..., description="예측 확신도 (0~1)")
