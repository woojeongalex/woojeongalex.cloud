from __future__ import annotations

from abc import ABC, abstractmethod


class GeminiPort(ABC):
    @abstractmethod
    def generate(self, message: str) -> str:
        pass
