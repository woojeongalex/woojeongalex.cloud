from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse


class JackTrainerPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: JackTrainerQuery) -> JackTrainerResponse:
        '''잭 도슨의 자기 소개 레포지토리 추상 메소드'''
        pass
