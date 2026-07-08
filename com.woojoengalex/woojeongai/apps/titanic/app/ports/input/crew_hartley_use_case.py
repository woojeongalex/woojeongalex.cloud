from abc import ABC, abstractmethod

import pandas as pd


class HartleyUseCase(ABC):
    @abstractmethod
    def correlation_graph(self, train_df: pd.DataFrame) -> bytes:
        pass
