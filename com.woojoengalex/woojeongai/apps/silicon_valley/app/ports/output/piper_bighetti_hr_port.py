from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse


class BighettiHrPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: BighettiHrQuery) -> BighettiHrResponse:
        '''넬슨 비게티의 자기 소개 레포지토리 추상 메소드'''
        pass
