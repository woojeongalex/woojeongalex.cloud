from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EmbarkedPort(str, Enum):
    CHERBOURG = "C"
    QUEENSTOWN = "Q"
    SOUTHAMPTON = "S"


@dataclass(frozen=True)
class Embarked:
    value: Optional[EmbarkedPort]

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Embarked":
        if not raw or not raw.strip():
            return cls(value=None)
        try:
            return cls(value=EmbarkedPort(raw.strip().upper()))
        except (ValueError, KeyError):
            raise ValueError(f"Embarked 유효하지 않은 값: '{raw}'")

    @property
    def is_unknown(self) -> bool:
        return self.value is None

    def __str__(self) -> str:
        return self.value.value if self.value is not None else ""
