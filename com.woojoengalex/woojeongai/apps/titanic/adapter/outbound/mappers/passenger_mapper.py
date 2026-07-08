from titanic.adapter.outbound.orm.passenger_orm import PersonOrm
from titanic.domain.entities.passenger_jack_trainer_entity import PassengerEntity
from titanic.domain.value_objects.passenger_vo import (
    Age,
    FamilyRelation,
    Gender,
    PassengerId,
    PassengerName,
    SurvivalStatus,
)


def orm_to_entity(orm: PersonOrm) -> PassengerEntity:
    return PassengerEntity(
        id=orm.id,
        passenger_id=PassengerId(str(orm.passenger_id)) if orm.passenger_id else None,
        name=PassengerName(orm.name) if orm.name else None,
        gender=Gender.from_raw(orm.gender),
        age=Age.from_raw(str(orm.age) if orm.age is not None else None),
        family_relation=FamilyRelation.from_raw(orm.sib_sp, orm.parch),
        survival_status=SurvivalStatus.from_raw(str(orm.survived) if orm.survived is not None else None),
    )


def entity_to_orm(entity: PassengerEntity, source_file: str = "") -> PersonOrm:
    survived_val = (
        "1" if entity.survival_status.survived is True
        else "0" if entity.survival_status.survived is False
        else ""
    )
    return PersonOrm(
        id=entity.id,
        source_file=source_file,
        passenger_id=str(entity.passenger_id) if entity.passenger_id else "",
        survived=survived_val,
        name=entity.name.full_name if entity.name else "",
        gender=entity.gender.value.value,
        age=str(entity.age.value) if not entity.age.is_unknown else "",
        sib_sp=str(entity.family_relation.sib_sp),
        parch=str(entity.family_relation.parch),
    )
