from titanic.adapter.outbound.orm.passenger_orm import PersonOrm
from titanic.domain.entities.passenger_rose_model_entity import RoseModelEntity


def orm_to_entity(orm: PersonOrm) -> RoseModelEntity:
    pass


def entity_to_orm(entity: RoseModelEntity) -> PersonOrm:
    pass
