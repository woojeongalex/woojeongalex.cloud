from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FamilyRelation:
    sib_sp: int
    parch: int

    def __post_init__(self) -> None:
        if self.sib_sp < 0:
            raise ValueError(f"sib_sp 유효하지 않은 값: '{self.sib_sp}'")
        if self.parch < 0:
            raise ValueError(f"parch 유효하지 않은 값: '{self.parch}'")

    @classmethod
    def from_raw(cls, sib_sp_raw: Optional[str], parch_raw: Optional[str]) -> "FamilyRelation":
        def _parse(val: Optional[str], field: str) -> int:
            if not val or not str(val).strip():
                return 0
            try:
                return int(str(val).strip())
            except (ValueError, TypeError):
                raise ValueError(f"{field} 유효하지 않은 값: '{val}'")

        return cls(sib_sp=_parse(sib_sp_raw, "sib_sp"), parch=_parse(parch_raw, "parch"))

    @property
    def total_family_size(self) -> int:
        return self.sib_sp + self.parch

    @property
    def family_size(self) -> int:
        return self.sib_sp + self.parch + 1

    @property
    def is_alone(self) -> bool:
        return self.sib_sp == 0 and self.parch == 0
