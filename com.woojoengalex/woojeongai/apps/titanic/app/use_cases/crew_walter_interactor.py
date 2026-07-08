import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_walter_schema import WalterSchema
from titanic.app.dtos.crew_walter_query import WalterPassengerPageDto, WalterQuery, WalterResponse
from titanic.app.ports.input.crew_walter_use_case import WalterUseCase
from titanic.app.ports.output.crew_walter_director_port import WalterDirectorPort

class WalterInteractor(WalterUseCase):

    def __init__(self, repository: WalterDirectorPort) -> None:
        self.repository = repository
    
    async def get_train_set(self) -> pd.DataFrame:
        return self.repository.get_train_set()

    async def get_test_set(self) -> pd.DataFrame:
        return self.repository.get_test_set()
        

    async def introduce_myself(self, schema: WalterSchema) -> WalterResponse:
        return await self.repository.introduce_myself(WalterQuery(
            id=schema.id,
            name=schema.name,
        ))

    async def read_passengers(
        self,
        source_file: str | None,
        page: int,
        size: int,
    ) -> WalterPassengerPageDto:
        return await self.repository.read_passengers(source_file, page, size)