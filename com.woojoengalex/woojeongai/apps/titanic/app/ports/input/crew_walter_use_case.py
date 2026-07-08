from abc import ABC, abstractmethod

import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_walter_schema import WalterSchema
from titanic.app.dtos.crew_walter_query import WalterPassengerPageDto, WalterResponse


class WalterUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: WalterSchema) -> WalterResponse:
        pass

    @abstractmethod
    async def get_train_set(self) -> pd.DataFrame:
        '''월터가 DB에서 train set을 가져오는 메소드'''
        pass

    @abstractmethod
    async def get_test_set(self) -> pd.DataFrame:
        '''월터가 DB에서 test set을 가져오는 메소드'''
        pass
    
    @abstractmethod
    async def read_passengers(
        self,
        source_file: str | None,
        page: int,
        size: int,
    ) -> WalterPassengerPageDto:
        pass
