from abc import ABC, abstractmethod

import pandas as pd

from titanic.app.dtos.crew_walter_query import WalterPassengerPageDto, WalterQuery, WalterResponse


class WalterDirectorPort(ABC):
    @abstractmethod
    def introduce_myself(self, query: WalterQuery) -> WalterResponse:
        pass

    @abstractmethod
    def get_train_set(self) -> pd.DataFrame:
        '''survived 컬럼이 있는 데이터 전체를 데이터프레임으로 반환하는 메소드'''
        pass

    @abstractmethod
    def get_test_set(self) -> pd.DataFrame:
        '''survived 컬럼이 없는 데이터 전체를 데이터프레임으로 반환하는 메소드'''
        pass

    @abstractmethod
    def read_passengers(
        self,
        source_file: str | None,
        page: int,
        size: int,
    ) -> WalterPassengerPageDto:
        pass
