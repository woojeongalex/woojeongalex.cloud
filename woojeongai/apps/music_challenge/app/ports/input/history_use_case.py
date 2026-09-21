from abc import ABC, abstractmethod

from music_challenge.app.dtos.history_dto import SubmissionHistoryItem


class GetMyHistoryUseCase(ABC):
    @abstractmethod
    async def get(self, username: str, limit: int) -> list[SubmissionHistoryItem]: ...
