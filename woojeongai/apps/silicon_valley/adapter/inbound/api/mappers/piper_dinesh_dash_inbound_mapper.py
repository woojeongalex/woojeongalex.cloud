"""DineshDash inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""

from silicon_valley.adapter.inbound.api.schemas.piper_dinesh_dash_schema import DineshDashSchema
from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery


def schema_to_query(schema: DineshDashSchema) -> DineshDashQuery:
    return DineshDashQuery(
        id=schema.id,
        name=schema.name,
    )
