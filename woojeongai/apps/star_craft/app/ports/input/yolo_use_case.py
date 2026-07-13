from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.yolo_dto import (
    YoloPredictCommand,
    YoloPredictResult,
    YoloTrainCommand,
    YoloTrainResult,
)


class YoloUseCase(ABC):
    """Inbound 입력 포트 — 사람 얼굴 인식(분류) YOLO 파인튜닝·추론."""

    @abstractmethod
    def execute(self, command: YoloTrainCommand) -> YoloTrainResult:
        """데이터셋을 로드하여 YOLO 분류 모델을 파인튜닝한다."""
        pass

    @abstractmethod
    def predict(self, command: YoloPredictCommand) -> YoloPredictResult:
        """업로드된 얼굴 이미지로 가장 유력한 인물을 예측한다."""
        pass
