from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClassificationVO:
    label: str
    confidence: float
    top5: list[tuple[str, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence는 0.0~1.0 사이여야 합니다: {self.confidence}")
