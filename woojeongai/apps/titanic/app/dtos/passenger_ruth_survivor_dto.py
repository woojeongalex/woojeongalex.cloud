from dataclasses import dataclass


@dataclass(frozen=True)
class RuthSurvivorQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RuthSurvivorResponse:
    id: int
    name: str
    role: str = ""
    description: str = ""
    ability: str = ""