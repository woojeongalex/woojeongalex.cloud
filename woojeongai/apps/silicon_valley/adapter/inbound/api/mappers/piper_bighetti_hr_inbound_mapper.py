"""BighettiHr inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""

from silicon_valley.adapter.inbound.api.schemas.piper_bighetti_hr_schema import BighettiHrSchema
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery


def schema_to_query(schema: BighettiHrSchema) -> BighettiHrQuery:
    return BighettiHrQuery(
        id=schema.id,
        name=schema.name,
    )
