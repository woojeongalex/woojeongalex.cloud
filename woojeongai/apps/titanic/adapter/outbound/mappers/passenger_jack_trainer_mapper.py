from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.domain.entities.passenger_jack_trainer_entity import PassengerEntity


class JackTrainerMapper:
    @staticmethod
    def to_entity(orm) -> PassengerEntity:
        return PassengerEntity.from_orm(orm)

    @staticmethod
    def to_orm(entity: PassengerEntity) -> JackTrainerOrm:
        # JackTrainerOrm PK는 passenger_id이며 id 컬럼 없음 → 버그: id 전달 시 TypeError
        raise TypeError("JackTrainerOrm has no 'id' column — pass passenger_id as PK instead")
