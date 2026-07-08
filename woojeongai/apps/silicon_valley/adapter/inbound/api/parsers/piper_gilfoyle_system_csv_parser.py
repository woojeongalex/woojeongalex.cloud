"""GilfoyleSystem upload CSV → 내부 타입 (무상태 파싱)."""

import csv
import io
import logging

from fastapi import HTTPException, UploadFile
from pydantic import ValidationError

from silicon_valley.adapter.inbound.api.schemas.piper_gilfoyle_system_schema import GilfoyleSystemSchema

log = logging.getLogger("silicon_valley")


class GilfoyleSystemCsvError(ValueError):
    pass


def parse_gilfoyle_system_csv(text: str) -> list[GilfoyleSystemSchema]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise GilfoyleSystemCsvError("CSV 헤더가 없습니다.")

    records = list(reader)
    if not records:
        raise GilfoyleSystemCsvError("CSV에 데이터 행이 없습니다.")

    try:
        return [GilfoyleSystemSchema.model_validate(row) for row in records]
    except ValidationError:
        raise


async def read_gilfoyle_system_upload(file: UploadFile) -> tuple[str, list[GilfoyleSystemSchema]]:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="업로드 파일이 비어 있습니다.")

    try:
        rows = parse_gilfoyle_system_csv(raw.decode("utf-8-sig", errors="replace"))
    except GilfoyleSystemCsvError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors()) from exc

    return file.filename or "upload.csv", rows
