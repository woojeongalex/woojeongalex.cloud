from __future__ import annotations

import io
import os

from PIL import Image
from ultralytics import YOLO

from star_craft.app.dtos.yolo_dto import (
    YoloPredictCommand,
    YoloPredictResult,
    YoloTrainCommand,
    YoloTrainResult,
)
from star_craft.app.ports.input.yolo_use_case import YoloUseCase
from star_craft.app.ports.output.yolo_model_port import YoloModelPort
from star_craft.app.ports.output.yolo_port import YoloPort

_BASE_MODEL = "yolo11n-cls.pt"


class YoloInteractor(YoloUseCase):

    def __init__(self, dataset: YoloPort, model: YoloModelPort) -> None:
        self._dataset = dataset
        self._model = model

    def execute(self, command: YoloTrainCommand) -> YoloTrainResult:
        dataset_root = self._dataset.get_dataset_root()
        classes = sorted(os.listdir(os.path.join(dataset_root, "train")))

        model = YOLO(_BASE_MODEL)
        model.train(
            data=dataset_root,
            epochs=command.epochs,
            batch=command.batch_size,
            imgsz=command.imgsz,
            device=command.device,
        )
        weights_path = self._model.save(str(model.trainer.best))
        return YoloTrainResult(
            dataset_root=dataset_root,
            epochs=command.epochs,
            classes=classes,
            weights_path=weights_path,
        )

    def predict(self, command: YoloPredictCommand) -> YoloPredictResult:
        weights_path = self._model.load_path()
        model = YOLO(weights_path)
        image = Image.open(io.BytesIO(command.image)).convert("RGB")

        results = model.predict(source=image, device=command.device, verbose=False)
        probs = results[0].probs
        top1 = int(probs.top1)
        return YoloPredictResult(
            name=results[0].names[top1],
            confidence=float(probs.top1conf),
        )
