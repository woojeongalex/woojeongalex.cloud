from dataclasses import dataclass


@dataclass(frozen=True)
class CalTestQuery:
    id: int
    name: str


@dataclass(frozen=True)
class CalTestResponse:
    id: int
    name: str
    role: str = ""
    description: str = ""
    ability: str = ""