from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_cal_tester_dto import CalTestQuery, CalTestResponse


class CalTestPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: CalTestQuery) -> CalTestResponse:
        '''칼 헉클리의 자기 소개 레포지토리 추상 메소드'''
        pass
