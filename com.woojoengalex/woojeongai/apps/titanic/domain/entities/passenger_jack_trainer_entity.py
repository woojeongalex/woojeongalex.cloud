from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from titanic.domain.value_objects.passenger_vo import (
    Age,
    FamilyRelation,
    Gender,
    PassengerId,
    PassengerName,
    SurvivalStatus,
)


@dataclass
class PassengerEntity:
    id: int
    passenger_id: Optional[PassengerId]
    name: Optional[PassengerName]
    gender: Gender
    age: Age
    family_relation: FamilyRelation
    survival_status: SurvivalStatus

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PassengerEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def is_high_risk(self) -> bool:
        if self.gender.is_female():
            return False
        if self.age.is_minor:
            return False
        if not self.family_relation.is_alone:
            return False
        return True

    def has_family(self) -> bool:
        return not self.family_relation.is_alone

    def record_survival(self, survived: bool) -> None:
        self.survival_status = SurvivalStatus(survived=survived)

    @classmethod
    def from_orm(cls, orm) -> PassengerEntity:
        return cls(
            id=orm.id,
            passenger_id=PassengerId(str(orm.passenger_id)) if orm.passenger_id is not None else None,
            name=PassengerName(orm.name) if orm.name is not None else None,
            gender=Gender.from_raw(orm.gender),
            age=Age.from_raw(str(orm.age) if orm.age is not None else None),
            family_relation=FamilyRelation.from_raw(orm.sib_sp, orm.parch),
            survival_status=SurvivalStatus.from_raw(str(orm.survived) if orm.survived is not None else None),
        )


# backward-compat aliases
TitanicPassenger = PassengerEntity
JackTrainerEntity = PassengerEntity
