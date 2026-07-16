from __future__ import annotations

from abc import ABC, abstractmethod


class JsonlExportPort(ABC):
    @abstractmethod
    def export(self, filename: str, rows: list[dict[str, str]]) -> str:
        """결과를 JSONL(한 줄당 JSON 객체 하나)로 저장하고 저장된 경로를 반환한다."""
        pass
