from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class DineshDashId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("DineshDashId는 양수여야 합니다.")
