from __future__ import annotations

from star_craft.adapter.inbound.api.schemas.convnext_schema import (
    ConvNextClassifyResponse,
)
from star_craft.app.dtos.convnext_dto import ClassifyCommand, ClassifyResponse


def schema_to_command(filename: str, content_type: str, data: bytes) -> ClassifyCommand:
    return ClassifyCommand(
        filename=filename, content_type=content_type, image_bytes=data
    )


def response_to_schema(dto: ClassifyResponse) -> ConvNextClassifyResponse:
    return ConvNextClassifyResponse(
        node_id=dto.node_id,
        label=dto.label,
        confidence=dto.confidence,
        queue_task_id=dto.queue_task_id,
    )
