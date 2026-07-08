from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.passenger_ruth_survivor_schema import RuthSurvivorSchema
from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorResponse


class RuthSurvivorUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RuthSurvivorSchema) -> RuthSurvivorResponse:
        '''루스 드윗 부카터의 자기소개 메소드'''
        pass
