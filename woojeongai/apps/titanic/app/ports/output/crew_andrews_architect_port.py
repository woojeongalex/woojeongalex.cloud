from abc import ABC, abstractmethod

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse


class AndrewsArchitectPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: AndrewsArchitectQuery) -> AndrewsArchitectResponse:
        pass
