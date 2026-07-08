"""Titanic inbound — HTTP·DB 경계 (라우터는 Use Case만 호출)."""

from titanic.adapter.inbound.api.mappers.james_inbound_mapper import (
    james_schema_to_person_command,
)
from titanic.adapter.inbound.api.schemas.crew_james_schema import JamesSchema, JamesUploadResponse
from titanic.app.ports.input.crew_james_use_case import JamesUseCase
from titanic.app.titanic_flow_log import titanic_flow_log


async def pass_james_upload(
    james: type[JamesUseCase],
    file_name: str,
    rows: list[JamesSchema],
) -> JamesUploadResponse:
    person_commands = [james_schema_to_person_command(row) for row in rows]
    result = await james.upload(person_commands, file_name)
    titanic_flow_log(
        "james-upload",
        "inbound",
        "Neon 저장 완료 file=%s saved=%s",
        file_name,
        result.get("count", len(rows)) if isinstance(result, dict) else len(rows),
        source_file=file_name,
    )
    if isinstance(result, dict):
        return JamesUploadResponse(**result)
    return JamesUploadResponse(file_name=file_name, count=len(rows))
