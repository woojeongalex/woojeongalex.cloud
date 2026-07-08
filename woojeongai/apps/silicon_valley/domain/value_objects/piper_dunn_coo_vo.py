from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class DunnCooId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("DunnCooId는 양수여야 합니다.")
