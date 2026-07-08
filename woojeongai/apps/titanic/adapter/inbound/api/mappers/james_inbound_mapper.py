"""James inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""

from titanic.adapter.inbound.api.schemas.crew_james_schema import JamesSchema
from titanic.app.dtos.crew_james_command import BookingCommand, PersonCommand


def james_schemas_to_person_commands(rows: list[JamesSchema]) -> list[PersonCommand]:
    return [james_schema_to_person_command(row) for row in rows]


def james_schema_to_person_command(row: JamesSchema) -> PersonCommand:
    return PersonCommand(
        passenger_id=row.passenger_id,
        survived=row.survived,
        pclass=row.pclass,
        name=row.name,
        gender=row.gender,
        age=row.age,
        sib_sp=row.sib_sp,
        parch=row.parch,
        ticket=row.ticket,
        fare=row.fare,
        cabin=row.cabin,
        embarked=row.embarked,
    )


def james_schema_to_booking_command(row: JamesSchema) -> BookingCommand:
    return BookingCommand(
        pclass=row.pclass,
        ticket=row.ticket,
        fare=row.fare,
        cabin=row.cabin,
        embarked=row.embarked,
    )
