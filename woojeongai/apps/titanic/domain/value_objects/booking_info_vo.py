from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from titanic.domain.value_objects.pclass_vo import PClass, PClassType
from titanic.domain.value_objects.embarked_vo import Embarked, EmbarkedPort


@dataclass(frozen=True)
class BookingInfo:
    pclass: PClass
    fare: Optional[float]
    embarked: Embarked

    def __post_init__(self) -> None:
        if self.fare is not None and self.fare < 0:
            raise ValueError(f"Fare 유효하지 않은 값: '{self.fare}'")

    @classmethod
    def from_raw(
        cls,
        pclass_raw: Optional[str],
        fare_raw: Optional[str],
        embarked_raw: Optional[str],
    ) -> "BookingInfo":
        fare: Optional[float] = None
        if fare_raw and fare_raw.strip():
            try:
                fare = float(fare_raw.strip())
            except (ValueError, TypeError):
                raise ValueError(f"Fare 유효하지 않은 값: '{fare_raw}'")

        return cls(
            pclass=PClass.from_raw(pclass_raw),
            fare=fare,
            embarked=Embarked.from_raw(embarked_raw),
        )

    @property
    def is_first_class(self) -> bool:
        return self.pclass.value == PClassType.FIRST

    @property
    def is_fare_unknown(self) -> bool:
        return self.fare is None

    @property
    def embarked_port(self) -> Optional[EmbarkedPort]:
        return self.embarked.value
