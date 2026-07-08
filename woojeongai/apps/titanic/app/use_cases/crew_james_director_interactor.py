from __future__ import annotations

from typing import Any

from titanic.app.dtos.crew_james_command import (
    BookingCommand,
    PersonCommand,
)
from titanic.app.dtos.crew_james_director_dto import (
    BookingCommand as DirectorBookingCommand,
    JamesDirectorQuery,
    JamesDirectorResponse,
    PersonCommand as DirectorPersonCommand,
)


class JamesDirectorInteractor:
    def __init__(self, repository) -> None:
        self.repository = repository

    async def introduce_myself(self, request) -> JamesDirectorResponse:
        return await self.repository.introduce_myself(JamesDirectorQuery(
            id=request.id,
            name=request.name,
        ))

    async def upload_titanic_file(self, rows: list) -> dict:
        person_commands = [
            DirectorPersonCommand(
                passenger_id=row.passenger_id or "",
                survived=row.survived if row.survived is not None else "",
                name=row.name or "",
                gender=row.gender or "",
                age=row.age or "",
                sib_sp=row.sib_sp or "",
                parch=row.parch or "",
            )
            for row in rows
        ]
        booking_commands = [
            DirectorBookingCommand(
                pclass=row.pclass or "",
                ticket=row.ticket or "",
                fare=row.fare or "",
                cabin=row.cabin if row.cabin is not None else "",
                embarked=row.embarked or "",
            )
            for row in rows
        ]
        count = await self.repository.receive_uploaded_records(person_commands, booking_commands)
        return {"saved": count}

    async def upload(self, person_commands: list[PersonCommand], file_name: str) -> dict[str, Any]:
        booking_commands = [
            BookingCommand(
                pclass=cmd.pclass,
                ticket=cmd.ticket,
                fare=cmd.fare,
                cabin=cmd.cabin,
                embarked=cmd.embarked,
            )
            for cmd in person_commands
        ]
        count = await self.repository.upload(person_commands, booking_commands, file_name)
        return {"saved": count}
