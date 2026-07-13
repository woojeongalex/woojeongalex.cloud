from __future__ import annotations

import logging

from star_craft.app.dtos.vision_dto import (
    VisionImageQuery,
    VisionImageResponse,
    VisionResponse,
    VisionQuery,
)
from star_craft.app.ports.output.vision_port import VisionPort
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class VisionRepository(VisionPort):
    """VisionPort 구현."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: VisionQuery) -> VisionResponse:
        logger.info(f"[VisionRepository] introduce_myself 진입 | request_data={schema}")
        reponse: VisionResponse = VisionResponse(
            id=schema.id * 10000,
            name=schema.name + "가 레포지토리에 다녀옴"
        )
        return reponse

    async def process_image(self, schema: VisionImageQuery) -> VisionImageResponse:
        logger.info(
            f"[VisionRepository] process_image 진입 | "
            f"filename={schema.filename} content_type={schema.content_type} size={schema.size}"
        )
        return VisionImageResponse(
            filename=schema.filename,
            content_type=schema.content_type,
            size=schema.size,
            message="이미지 접수 완료 (비전 처리 로직은 아직 미구현)",
            url="",
        )
