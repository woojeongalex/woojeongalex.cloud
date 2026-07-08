from dataclasses import dataclass


@dataclass(frozen=True)
class GilfoyleSystemQuery:
    id: int
    name: str


@dataclass(frozen=True)
class GilfoyleSystemResponse:
    id: int
    name: str
    role: str = ""
    description: str = ""
    ability: str = ""
