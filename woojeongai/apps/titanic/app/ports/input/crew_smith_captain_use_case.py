from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse


class SmithCaptainUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        pass

    @abstractmethod
    async def chat(self, schema: ChatSchema) -> SmithCaptainResponse:
        '''사용자 자연어 입력을 받아 채팅 응답을 반환'''
        pass
