from abc import ABC, abstractmethod

import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatResponse


class LoweBoatUseCase(ABC):
    @abstractmethod
    def feature_engineering(self, train_set: pd.DataFrame, test_set: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list]:
        pass

    @abstractmethod
    async def introduce_myself(self, schema: LoweBoatSchema) -> LoweBoatResponse:
        pass
