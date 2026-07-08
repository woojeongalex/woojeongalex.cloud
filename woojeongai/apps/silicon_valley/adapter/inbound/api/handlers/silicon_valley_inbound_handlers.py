"""Silicon Valley inbound — HTTP·DB 경계 (라우터는 Use Case만 호출)."""

from silicon_valley.adapter.inbound.api.mappers.piper_bighetti_hr_inbound_mapper import schema_to_query as bighetti_schema_to_query
from silicon_valley.adapter.inbound.api.schemas.piper_bighetti_hr_schema import BighettiHrSchema
from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase


async def pass_bighetti_introduce(
    bighetti: BighettiHrUseCase,
    schema: BighettiHrSchema,
) -> object:
    query = bighetti_schema_to_query(schema)
    return await bighetti.introduce_myself(query)
