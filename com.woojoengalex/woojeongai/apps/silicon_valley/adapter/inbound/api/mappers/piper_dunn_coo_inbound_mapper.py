"""DunnCoo inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""

from silicon_valley.adapter.inbound.api.schemas.piper_dunn_coo_schema import DunnCooSchema
from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery


def schema_to_query(schema: DunnCooSchema) -> DunnCooQuery:
    return DunnCooQuery(
        id=schema.id,
        name=schema.name,
    )
