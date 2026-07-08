from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashResponse


class DineshDashUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, request: Any) -> DineshDashResponse:
        pass

    @abstractmethod
    async def get_dashboard_data(self) -> dict[str, Any]:
        '''디네시가 담당하는 대시보드 데이터를 반환하는 메소드'''
        return {}
