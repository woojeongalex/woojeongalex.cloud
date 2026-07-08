from titanic.adapter.outbound.orm.booking_orm import BookingOrm
from titanic.app.dtos.crew_james_command import BookingCommand


def orm_to_command(orm: BookingOrm) -> BookingCommand:
    return BookingCommand(
        pclass=orm.pclass,
        ticket=orm.ticket,
        fare=orm.fare,
        cabin=orm.cabin,
        embarked=orm.embarked,
    )


def command_to_orm(person_id: int, command: BookingCommand) -> BookingOrm:
    return BookingOrm(
        person_id=person_id,
        pclass=command.pclass,
        ticket=command.ticket,
        fare=command.fare,
        cabin=command.cabin,
        embarked=command.embarked,
    )
