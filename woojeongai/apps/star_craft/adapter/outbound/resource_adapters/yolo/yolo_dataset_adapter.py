from __future__ import annotations

import os

from star_craft.app.ports.output.yolo_port import YoloPort


class YoloDatasetAdapter(YoloPort):
    """로컬 디렉토리(train/<사람이름>/*.jpg, val/<사람이름>/*.jpg)에서 얼굴 분류 데이터셋을 제공한다."""

    def __init__(self, base_path: str) -> None:
        self._base_path = base_path

    def get_dataset_root(self) -> str:
        train_dir = os.path.join(self._base_path, "train")
        val_dir = os.path.join(self._base_path, "val")
        if not os.path.isdir(train_dir) or not os.path.isdir(val_dir):
            raise FileNotFoundError(
                f"YOLO 분류 데이터셋을 찾을 수 없습니다: {train_dir}, {val_dir} 에 "
                "인물별 하위 폴더(예: train/ben_afflek/*.jpg)를 채워주세요."
            )
        return self._base_path
