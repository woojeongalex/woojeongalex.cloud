from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.convnext_dto import ClassifyCommand, ClassifyResponse


class ConvNextAgentUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/convnext_router.py 와 대응."""

    @abstractmethod
    async def classify_and_store(self, cmd: ClassifyCommand) -> ClassifyResponse:
        """이미지를 분류하고 결과를 그래프 DB·큐에 저장한다."""
        pass
