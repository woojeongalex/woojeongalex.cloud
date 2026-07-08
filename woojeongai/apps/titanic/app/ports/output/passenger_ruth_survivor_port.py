from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorQuery, RuthSurvivorResponse


class RuthSurvivorPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RuthSurvivorQuery) -> RuthSurvivorResponse:
        '''루스 드윗 부카터의 자기 소개 레포지토리 추상 메소드'''
        pass
