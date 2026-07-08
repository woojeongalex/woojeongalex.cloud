"""James upload — `Titanic-Dataset.csv` 기준 Use Case Command DTO.

- HTTP(Pydantic)와 분리: `adapter/inbound/api/mappers/james_inbound_mapper.py`
- Neon 저장: `PersonCommand` → `person_orm`, `BookingCommand` → `booking_orm`
"""

__all__ = ["PERSON_COMMAND_FIELDS", "BookingCommand", "PersonCommand", "JamesQuery", "JamesIntroduceResponse"]
from dataclasses import dataclass, field
from typing import Optional

from titanic.app.dtos.passenger_row import PassengerRowDto

# PersonCommand 필드 순서 = CSV snake_case (Titanic-Dataset.csv)
PERSON_COMMAND_FIELDS: tuple[str, ...] = (
    "passenger_id",
    "survived",
    "pclass",
    "name",
    "gender",
    "age",
    "sib_sp",
    "parch",
    "ticket",
    "fare",
    "cabin",
    "embarked",
)


@dataclass
class PersonCommand:
    """CSV 1행 = Person + Booking + Port(country 제외) 역정규화."""

    passenger_id: Optional[str] = field(default=None)
    survived: Optional[str] = field(default=None)
    pclass: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    gender: Optional[str] = field(default=None)
    age: Optional[str] = field(default=None)
    sib_sp: Optional[str] = field(default=None)
    parch: Optional[str] = field(default=None)
    ticket: Optional[str] = field(default=None)
    fare: Optional[str] = field(default=None)
    cabin: Optional[str] = field(default=None)
    embarked: Optional[str] = field(default=None)

    def to_passenger_row(self) -> PassengerRowDto:
        return PassengerRowDto(
            passenger_id=self.passenger_id,
            survived=self.survived,
            pclass=self.pclass,
            name=self.name,
            gender=self.gender,
            age=self.age,
            sib_sp=self.sib_sp,
            parch=self.parch,
            ticket=self.ticket,
            fare=self.fare,
            cabin=self.cabin,
            embarked=self.embarked,
        )


@dataclass
class BookingCommand:
    """Booking + Port(embarked만) — `Titanic-Dataset.csv`에 있는 컬럼만."""

    pclass: Optional[str] = field(default=None)
    ticket: Optional[str] = field(default=None)
    fare: Optional[str] = field(default=None)
    cabin: Optional[str] = field(default=None)
    embarked: Optional[str] = field(default=None)


@dataclass(frozen=True)
class JamesQuery:
    id: int
    name: str


@dataclass(frozen=True)
class JamesIntroduceResponse:
    id: int
    name: str
