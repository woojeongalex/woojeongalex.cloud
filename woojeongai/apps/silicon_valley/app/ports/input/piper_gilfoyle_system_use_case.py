from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemResponse


class GilfoyleSystemUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, request: Any) -> GilfoyleSystemResponse:
        pass

    @abstractmethod
    async def monitor_system(self) -> dict[str, Any]:
        '''길포일이 담당하는 시스템 인프라 상태를 반환하는 메소드'''
        return {}
