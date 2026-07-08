"""GilfoyleSystem inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""

from silicon_valley.adapter.inbound.api.schemas.piper_gilfoyle_system_schema import GilfoyleSystemSchema
from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemQuery


def schema_to_query(schema: GilfoyleSystemSchema) -> GilfoyleSystemQuery:
    return GilfoyleSystemQuery(
        id=schema.id,
        name=schema.name,
    )
