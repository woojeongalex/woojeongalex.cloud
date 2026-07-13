from __future__ import annotations
from dataclasses import dataclass


@dataclass
class VisionEntity:
    """동등성은 id 기준."""

    id: int
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VisionEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_orm(cls, orm: object) -> "VisionEntity":
        return cls(
            id=orm.id,
            name=orm.name or "unknown",
        )

    def full_name(self) -> str:
        return self.name
