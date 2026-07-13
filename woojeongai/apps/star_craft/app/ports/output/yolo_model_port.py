from __future__ import annotations

from abc import ABC, abstractmethod


class YoloModelPort(ABC):

    @abstractmethod
    def save(self, trained_weights_path: str) -> str:
        """학습 직후 생성된 가중치를 정본 위치로 저장하고 그 경로를 반환한다."""
        pass

    @abstractmethod
    def load_path(self) -> str:
        """추론에 사용할 정본 가중치 경로를 반환한다. 없으면 예외를 던진다."""
        pass
