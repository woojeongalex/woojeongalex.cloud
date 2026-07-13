from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.vision_dto import (
    VisionImageQuery,
    VisionImageResponse,
    VisionQuery,
    VisionResponse,
)


class VisionUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/vision_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: VisionQuery) -> VisionResponse:
        """Vision을 조회한다."""
        pass

    @abstractmethod
    async def process_image(self, schema: VisionImageQuery) -> VisionImageResponse:
        """업로드된 이미지를 수신한다 (현재는 접수 확인만, 실제 비전 처리는 미구현)."""
        pass
