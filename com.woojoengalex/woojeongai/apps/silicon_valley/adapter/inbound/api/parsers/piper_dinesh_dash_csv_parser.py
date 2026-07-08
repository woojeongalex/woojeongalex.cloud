"""DineshDash upload CSV → 내부 타입 (무상태 파싱)."""

import csv
import io
import logging

from fastapi import HTTPException, UploadFile
from pydantic import ValidationError

from silicon_valley.adapter.inbound.api.schemas.piper_dinesh_dash_schema import DineshDashSchema

log = logging.getLogger("silicon_valley")


class DineshDashCsvError(ValueError):
    pass


def parse_dinesh_dash_csv(text: str) -> list[DineshDashSchema]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise DineshDashCsvError("CSV 헤더가 없습니다.")

    records = list(reader)
    if not records:
        raise DineshDashCsvError("CSV에 데이터 행이 없습니다.")

    try:
        return [DineshDashSchema.model_validate(row) for row in records]
    except ValidationError:
        raise


async def read_dinesh_dash_upload(file: UploadFile) -> tuple[str, list[DineshDashSchema]]:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="업로드 파일이 비어 있습니다.")

    try:
        rows = parse_dinesh_dash_csv(raw.decode("utf-8-sig", errors="replace"))
    except DineshDashCsvError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors()) from exc

    return file.filename or "upload.csv", rows
