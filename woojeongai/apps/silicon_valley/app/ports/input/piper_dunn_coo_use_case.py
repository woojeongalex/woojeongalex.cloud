from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooResponse


class DunnCooUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, request: Any) -> DunnCooResponse:
        pass

    @abstractmethod
    async def manage_operations(self) -> dict[str, Any]:
        '''자레드가 담당하는 운영 현황을 반환하는 메소드'''
        return {}
