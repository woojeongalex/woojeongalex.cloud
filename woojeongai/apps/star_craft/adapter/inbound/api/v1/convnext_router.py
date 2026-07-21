from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from star_craft.adapter.inbound.api.deps.convnext_deps import get_convnext_use_case
from star_craft.adapter.inbound.api.mappers.convnext_mapper import (
    response_to_schema,
    schema_to_command,
)
from star_craft.adapter.inbound.api.schemas.convnext_schema import (
    ConvNextClassifyResponse,
)
from star_craft.app.ports.input.convnext_agent_use_case import ConvNextAgentUseCase

convnext_router = APIRouter(prefix="/convnext", tags=["convnext"])


@convnext_router.post(
    "/classify",
    response_model=ConvNextClassifyResponse,
    summary="ConvNeXt Nano 이미지 분류",
)
async def classify_image(
    file: UploadFile = File(...),
    use_case: ConvNextAgentUseCase = Depends(get_convnext_use_case),
) -> ConvNextClassifyResponse:
    data = await file.read()
    cmd = schema_to_command(
        file.filename or "unknown",
        file.content_type or "application/octet-stream",
        data,
    )
    result = await use_case.classify_and_store(cmd)
    return response_to_schema(result)
