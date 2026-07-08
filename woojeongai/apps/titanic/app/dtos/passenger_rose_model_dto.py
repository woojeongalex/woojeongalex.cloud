from dataclasses import dataclass


@dataclass(frozen=True)
class RoseModelQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RoseModelResponse:
    id: int
    name: str
    role: str = ""
    description: str = ""
    ability: str = ""