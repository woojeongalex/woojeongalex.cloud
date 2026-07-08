"""[Layer: Use Cases] 업로드 승객 1행 DTO — HTTP/ORM과 분리."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PassengerRowDto:
    passenger_id: Optional[str] = field(default=None)
    survived: Optional[str] = field(default=None)
    pclass: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    gender: Optional[str] = field(default=None)
    age: Optional[str] = field(default=None)
    sib_sp: Optional[str] = field(default=None)
    parch: Optional[str] = field(default=None)
    ticket: Optional[str] = field(default=None)
    fare: Optional[str] = field(default=None)
    cabin: Optional[str] = field(default=None)
    embarked: Optional[str] = field(default=None)
