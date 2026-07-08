from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

import pandas as pd

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelResponse


class PredictionStrategy(Protocol):
    def predict(self, keywords: list[str]) -> float: ...


class RoseModelUseCase(ABC):

    @abstractmethod
    async def predict(self, keywords: list[str]) -> float:
        pass

    @abstractmethod
    async def train_model(self, train_set: pd.DataFrame) -> dict[str, Any]:
        '''훈련 데이터로 10개 전략을 평가하고 최적 전략을 선택하는 메소드'''
        pass

    @abstractmethod
    def analyze_and_answer(
        self,
        intent: str,
        question: str,
        keywords: list[str],
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        survival_prob: float,
        best_strategy: str,
        best_accuracy: float,
    ) -> str:
        pass

    @abstractmethod
    async def introduce_myself(self, schema: RoseModelSchema) -> RoseModelResponse:
        pass
