from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.theone_base import Base
from titanic.app.dtos.crew_james_command import BookingCommand


class BookingOrm(Base):
    __tablename__ = "titanic_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("titanic_passengers.id"), index=True)
    pclass: Mapped[str] = mapped_column(String(8), nullable=True)
    ticket: Mapped[str] = mapped_column(String(64), nullable=True)
    fare: Mapped[str] = mapped_column(String(32), nullable=True)
    cabin: Mapped[str] = mapped_column(String(64), nullable=True)
    embarked: Mapped[str] = mapped_column(String(8), nullable=True)

    @classmethod
    def from_command(cls, person_id: int, command: BookingCommand) -> "BookingOrm":
        return cls(
            person_id=person_id,
            pclass=command.pclass,
            ticket=command.ticket,
            fare=command.fare,
            cabin=command.cabin,
            embarked=command.embarked,
        )
