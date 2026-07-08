from fastapi import APIRouter, Depends, File, UploadFile

from titanic.adapter.inbound.api.mappers.james_inbound_mapper import james_schemas_to_person_commands
from titanic.adapter.inbound.api.parsers.james_csv_parser import read_james_upload
from titanic.adapter.inbound.api.schemas.crew_james_introduce_schema import JamesIntroduceSchema
from titanic.adapter.inbound.api.schemas.crew_james_schema import JamesUploadResponse
from titanic.app.dtos.crew_james_command import JamesIntroduceResponse
from titanic.app.ports.input.crew_james_use_case import JamesUseCase
from titanic.dependencies.crew_james_provider import get_james_use_case

james_router = APIRouter(prefix="/james", tags=["james"])


@james_router.get("/myself")
async def introduce_myself(
    james: JamesUseCase = Depends(get_james_use_case),
) -> JamesIntroduceResponse:
    return await james.introduce_myself(
        JamesIntroduceSchema(id=1, name="제임스 카메론 (James Cameron)")
    )


@james_router.post("/upload", response_model=JamesUploadResponse)
async def upload_titanic_csv(
    file: UploadFile = File(...),
    james: JamesUseCase = Depends(get_james_use_case),
) -> JamesUploadResponse:
    file_name, rows = await read_james_upload(file)
    result = await james.upload(
        james_schemas_to_person_commands(rows),
        file_name,
    )
    return JamesUploadResponse(**result)
