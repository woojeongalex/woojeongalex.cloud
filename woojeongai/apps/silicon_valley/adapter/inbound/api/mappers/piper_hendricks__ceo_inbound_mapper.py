"""HendricksCeo inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""

from silicon_valley.adapter.inbound.api.schemas.piper_hendricks__ceo_schema import HendricksCeoSchema
from silicon_valley.app.dtos.piper_hendricks__ceo_dto import HendricksCeoQuery


def schema_to_query(schema: HendricksCeoSchema) -> HendricksCeoQuery:
    return HendricksCeoQuery(
        id=schema.id,
        name=schema.name,
    )
