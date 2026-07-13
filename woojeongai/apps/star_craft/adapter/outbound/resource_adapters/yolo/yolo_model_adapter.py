from __future__ import annotations

import os
import shutil

from star_craft.app.ports.output.yolo_model_port import YoloModelPort


class YoloModelAdapter(YoloModelPort):
    """학습된 가중치를 로컬 디렉토리의 고정 경로(정본)에 보관한다."""

    def __init__(self, model_path: str) -> None:
        self._model_path = model_path

    def save(self, trained_weights_path: str) -> str:
        os.makedirs(os.path.dirname(self._model_path), exist_ok=True)
        shutil.copyfile(trained_weights_path, self._model_path)
        return self._model_path

    def load_path(self) -> str:
        if not os.path.exists(self._model_path):
            raise FileNotFoundError(
                f"학습된 가중치가 없습니다: {self._model_path} — 먼저 /vision/yolo-train으로 학습을 실행하세요."
            )
        return self._model_path
