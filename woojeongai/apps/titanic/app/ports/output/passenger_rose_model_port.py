from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse


class RoseModelPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RoseModelQuery) -> RoseModelResponse:
        '''로즈 드윗 부카터의 자기 소개 레포지토리 추상 메소드'''
        pass
