from __future__ import annotations

from abc import ABC, abstractmethod


class YoloPort(ABC):

    @abstractmethod
    def get_dataset_root(self) -> str:
        """train/val 하위에 인물별 폴더(예: train/ben_afflek/*.jpg)를 담은 데이터셋 루트 경로를 반환한다."""
        pass
