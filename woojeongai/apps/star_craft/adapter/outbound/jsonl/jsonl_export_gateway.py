from __future__ import annotations

import json
import logging
import os

from star_craft.app.ports.output.jsonl_export_port import JsonlExportPort

logger = logging.getLogger(__name__)


class JsonlExportGateway(JsonlExportPort):
    """수집 결과를 JSONL(한 줄당 JSON 객체 하나) 파일로 저장한다.
    크롤러·스크래퍼가 각자 다른 output_dir로 인스턴스를 생성해 쓴다."""

    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def export(self, filename: str, rows: list[dict[str, str]]) -> str:
        os.makedirs(self._output_dir, exist_ok=True)
        path = os.path.join(self._output_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        logger.info(f"[JsonlExportGateway] {len(rows)}건 저장 | path={path}")
        return path
