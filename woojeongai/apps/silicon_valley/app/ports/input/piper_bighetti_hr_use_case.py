from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse


class BighettiHrUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, request: Any) -> BighettiHrResponse:
        pass

    @abstractmethod
    async def get_employee_list(self) -> dict[str, Any]:
        '''파이드 파이퍼 팀원 목록을 반환하는 메소드'''
        return {}
