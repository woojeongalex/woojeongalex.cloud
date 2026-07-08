from abc import ABC, abstractmethod

from titanic.app.dtos.crew_james_command import BookingCommand, JamesIntroduceResponse, JamesQuery, PersonCommand


class JamesPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: JamesQuery) -> JamesIntroduceResponse:
        pass

    @abstractmethod
    async def upload(
        self,
        person_commands: list[PersonCommand],
        booking_commands: list[BookingCommand],
        file_name: str,
    ) -> int:
        pass
