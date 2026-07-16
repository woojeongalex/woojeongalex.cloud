from __future__ import annotations

from abc import ABC, abstractmethod


class CsvExportPort(ABC):
    @abstractmethod
    def export(self, filename: str, rows: list[dict[str, str]]) -> str:
        """결과를 CSV로 저장하고 저장된 경로를 반환한다."""
        pass
