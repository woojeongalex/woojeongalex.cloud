"""James upload CSV → `JamesSchema` 목록 (무상태 파싱)."""

import csv
import io
import logging

from fastapi import HTTPException, UploadFile
from pydantic import ValidationError

from titanic.adapter.inbound.api.schemas.crew_james_schema import JamesSchema

log = logging.getLogger("titanic")


class JamesCsvError(ValueError):
    pass


def parse_james_csv(text: str) -> list[JamesSchema]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise JamesCsvError("CSV 헤더가 없습니다.")

    records = list(reader)
    if not records:
        raise JamesCsvError("CSV에 데이터 행이 없습니다.")

    try:
        return [JamesSchema.model_validate(row) for row in records]
    except ValidationError:
        raise


async def read_james_upload(file: UploadFile) -> tuple[str, list[JamesSchema]]:
    """업로드 파일 검증·디코딩·CSV 파싱 (무상태). 실패 시 HTTP 400."""
    log.info("[parser] filename=%r content_type=%r", file.filename, file.content_type)

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="업로드 파일이 비어 있습니다.")

    try:
        rows = parse_james_csv(raw.decode("utf-8-sig", errors="replace"))
    except JamesCsvError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors()) from exc

    return file.filename or "upload.csv", rows
