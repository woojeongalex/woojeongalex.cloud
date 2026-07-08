from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from titanic.domain.value_objects.family_relation_vo import FamilyRelation


class GenderType(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class SurvivedType(int, Enum):
    DIED = 0
    SURVIVED = 1


@dataclass(frozen=True)
class PassengerId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PassengerId 빈 값은 허용되지 않습니다.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PassengerName:
    full_name: str

    def __post_init__(self) -> None:
        if not self.full_name or not self.full_name.strip():
            raise ValueError("PassengerName 빈 값은 허용되지 않습니다.")
        if len(self.full_name) > 200:
            raise ValueError("PassengerName은 200자를 초과할 수 없습니다.")

    @property
    def normalized(self) -> str:
        return self.full_name.strip()


@dataclass(frozen=True)
class Gender:
    value: GenderType

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Gender":
        if not raw or not raw.strip():
            return cls(value=GenderType.UNKNOWN)
        normalized = raw.strip().lower()
        if normalized == "male":
            return cls(value=GenderType.MALE)
        if normalized == "female":
            return cls(value=GenderType.FEMALE)
        return cls(value=GenderType.UNKNOWN)

    def is_female(self) -> bool:
        return self.value == GenderType.FEMALE

    def __str__(self) -> str:
        return self.value.value


@dataclass(frozen=True)
class Age:
    value: Optional[float]

    def __post_init__(self) -> None:
        if self.value is not None:
            if self.value < 0 or self.value > 120:
                raise ValueError(f"Age 유효하지 않은 값: '{self.value}'")

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Age":
        if not raw or not raw.strip():
            return cls(value=None)
        try:
            return cls(value=float(raw.strip()))
        except (ValueError, TypeError):
            raise ValueError(f"Age 파싱 실패: '{raw}'")

    @property
    def is_unknown(self) -> bool:
        return self.value is None

    @property
    def is_minor(self) -> bool:
        return self.value is not None and self.value < 18

    def __str__(self) -> str:
        return str(self.value) if self.value is not None else ""


@dataclass(frozen=True)
class SurvivalStatus:
    survived: Optional[bool]

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "SurvivalStatus":
        if not raw or not raw.strip():
            return cls(survived=None)
        try:
            v = int(raw.strip())
            if v not in (0, 1):
                raise ValueError
            return cls(survived=bool(v))
        except (ValueError, TypeError):
            raise ValueError(f"SurvivalStatus 파싱 실패: '{raw}'")

    @property
    def is_unknown(self) -> bool:
        return self.survived is None


__all__ = [
    "GenderType",
    "SurvivedType",
    "PassengerId",
    "PassengerName",
    "Gender",
    "Age",
    "FamilyRelation",
    "SurvivalStatus",
]
