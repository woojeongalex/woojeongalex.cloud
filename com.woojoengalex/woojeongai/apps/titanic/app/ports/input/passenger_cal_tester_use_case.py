from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTestSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTestResponse


class CalTestUseCase(ABC):

    @abstractmethod
    async def test_models(self, test_set: dict[str, Any]) -> dict[str, Any]:
        '''잭이 훈련한 모델들을 칼이 테스트하는 메소드'''
        pass

    @abstractmethod
    async def introduce_myself(self, schema: CalTestSchema) -> CalTestResponse:
        '''칼 테스터의 자기소개 메소드'''
        pass
