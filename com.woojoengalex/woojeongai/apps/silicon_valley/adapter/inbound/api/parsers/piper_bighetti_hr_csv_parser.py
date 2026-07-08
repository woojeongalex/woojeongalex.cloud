"""BighettiHr upload CSV → 내부 타입 (무상태 파싱)."""

import csv
import io
import logging

from fastapi import HTTPException, UploadFile
from pydantic import ValidationError

from silicon_valley.adapter.inbound.api.schemas.piper_bighetti_hr_schema import BighettiHrSchema

log = logging.getLogger("silicon_valley")


class BighettiHrCsvError(ValueError):
    pass


def parse_bighetti_hr_csv(text: str) -> list[BighettiHrSchema]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise BighettiHrCsvError("CSV 헤더가 없습니다.")

    records = list(reader)
    if not records:
        raise BighettiHrCsvError("CSV에 데이터 행이 없습니다.")

    try:
        return [BighettiHrSchema.model_validate(row) for row in records]
    except ValidationError:
        raise


async def read_bighetti_hr_upload(file: UploadFile) -> tuple[str, list[BighettiHrSchema]]:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="업로드 파일이 비어 있습니다.")

    try:
        rows = parse_bighetti_hr_csv(raw.decode("utf-8-sig", errors="replace"))
    except BighettiHrCsvError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors()) from exc

    return file.filename or "upload.csv", rows
