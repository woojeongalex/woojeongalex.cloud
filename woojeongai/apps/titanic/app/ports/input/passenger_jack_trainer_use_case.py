from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse


class JackTrainerUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, request: Any) -> JackTrainerResponse:
        pass

    @abstractmethod
    async def get_model_train(self) -> dict[str, Any]:
        '''로즈가 제안한 모델들의 매니페스트를 반환하는 메소드'''
        pass

    @abstractmethod
    async def train_model(self, train_set: pd.DataFrame) -> dict[str, Any]:
        '''로즈가 제안한 10개 sklearn 모델을 실제 훈련 데이터로 학습시키는 메소드'''
        pass
