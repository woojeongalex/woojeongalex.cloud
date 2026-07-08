from dataclasses import dataclass


@dataclass(frozen=True)
class JamesDirectorQuery:
    id: int
    name: str


@dataclass(frozen=True)
class JamesDirectorResponse:
    answer: str


@dataclass(frozen=True)
class PersonCommand:
    passenger_id: str
    survived: str
    name: str
    gender: str
    age: str
    sib_sp: str
    parch: str


@dataclass(frozen=True)
class BookingCommand:
    pclass: str
    ticket: str
    fare: str
    cabin: str
    embarked: str
