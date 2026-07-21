from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.orm.booking_orm import BookingOrm
from titanic.adapter.outbound.orm.passenger_orm import PersonOrm
from titanic.app.dtos.crew_james_command import BookingCommand, JamesIntroduceResponse, JamesQuery, PersonCommand
from titanic.app.ports.output.crew_james_port import JamesPort

logger = logging.getLogger(__name__)


class JamesRepository(JamesPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: JamesQuery) -> JamesIntroduceResponse:
        logger.info(f"[JamesRepository] introduce_myself 진입 | request_data={query}")
        response: JamesIntroduceResponse = JamesIntroduceResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
        return response

    async def upload(
        self,
        person_commands: list[PersonCommand],
        booking_commands: list[BookingCommand],
        file_name: str,
    ) -> int:
        existing_passenger_ids: set[str] = set(
            (
                await self.session.execute(select(PersonOrm.passenger_id))
            ).scalars().all()
        )

        new_pairs = [
            (pc, bc)
            for pc, bc in zip(person_commands, booking_commands)
            if pc.passenger_id not in existing_passenger_ids
        ]
        if not new_pairs:
            return 0

        person_orms = [
            PersonOrm(
                source_file=file_name,
                passenger_id=cmd.passenger_id,
                name=cmd.name,
                gender=cmd.gender,
                age=cmd.age,
                sib_sp=cmd.sib_sp,
                parch=cmd.parch,
                survived=cmd.survived,
            )
            for cmd, _ in new_pairs
        ]
        self.session.add_all(person_orms)
        await self.session.flush()

        booking_orms = [
            BookingOrm(
                person_id=person_orm.id,
                pclass=bc.pclass,
                ticket=bc.ticket,
                fare=bc.fare,
                cabin=bc.cabin,
                embarked=bc.embarked,
            )
            for person_orm, (_, bc) in zip(person_orms, new_pairs)
        ]
        self.session.add_all(booking_orms)
        await self.session.commit()

        return len(person_orms)