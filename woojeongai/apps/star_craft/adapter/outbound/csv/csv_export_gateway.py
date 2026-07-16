from __future__ import annotations

import csv
import logging
import os

from star_craft.app.ports.output.csv_export_port import CsvExportPort

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "exports"
)


class CsvExportGateway(CsvExportPort):
    """수집 결과를 CSV 파일로 저장한다."""

    def __init__(self, output_dir: str | None = None):
        self._output_dir = output_dir or _DEFAULT_OUTPUT_DIR

    def export(self, filename: str, rows: list[dict[str, str]]) -> str:
        os.makedirs(self._output_dir, exist_ok=True)
        path = os.path.join(self._output_dir, filename)

        if not rows:
            open(path, "w", encoding="utf-8-sig").close()
            logger.info(f"[CsvExportGateway] 결과 없음, 빈 파일 저장 | path={path}")
            return path

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"[CsvExportGateway] {len(rows)}건 저장 | path={path}")
        return path
