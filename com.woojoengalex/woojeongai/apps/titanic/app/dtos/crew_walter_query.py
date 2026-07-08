"""[Layer: Use Cases] Walter 조회 DTO."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WalterQuery:
    id: int
    name: str


@dataclass(frozen=True)
class WalterResponse:
    id: int
    name: str


@dataclass
class WalterPassengerPageDto:
    source_file: str | None
    page: int
    size: int
    total: int
    total_pages: int
    rows: list[dict[str, Any]]
