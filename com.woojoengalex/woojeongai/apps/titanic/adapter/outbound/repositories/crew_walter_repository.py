from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import core.matrix.database_manager as _db_manager

from titanic.adapter.outbound.orm.booking_orm import BookingOrm
from titanic.adapter.outbound.orm.passenger_orm import PersonOrm
from titanic.app.dtos.crew_walter_query import WalterPassengerPageDto, WalterQuery, WalterResponse
from titanic.app.ports.output.crew_walter_director_port import WalterDirectorPort

logger = logging.getLogger(__name__)


def _row_to_dict(person: PersonOrm, booking: BookingOrm | None) -> dict[str, Any]:
    return {
        "id": person.id,
        "passenger_id": person.passenger_id,
        "survived": person.survived,
        "pclass": booking.pclass if booking else None,
        "name": person.name,
        "gender": person.gender,
        "age": person.age,
        "sib_sp": person.sib_sp,
        "parch": person.parch,
        "ticket": booking.ticket if booking else None,
        "fare": booking.fare if booking else None,
        "cabin": booking.cabin if booking else None,
        "embarked": booking.embarked if booking else None,
        "source_file": person.source_file,
    }


def _to_sync_url(async_url: str) -> str:
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")


class WalterRepository(WalterDirectorPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _sync_engine(self):
        raw_url = _db_manager.engine.url.render_as_string(hide_password=False)
        return create_engine(_to_sync_url(raw_url))

    def get_train_set(self) -> pd.DataFrame:
        return pd.read_sql(
            "SELECT * FROM titanic_passengers WHERE survived IS NOT NULL",
            self._sync_engine(),
        )

    def get_test_set(self) -> pd.DataFrame:
        return pd.read_sql(
            "SELECT * FROM titanic_passengers WHERE survived IS NULL",
            self._sync_engine(),
        )

    async def introduce_myself(self, query: WalterQuery) -> WalterResponse:
        logger.info(f"[WalterRepository] introduce_myself 진입 | request_data={query}")
        response: WalterResponse = WalterResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
        return response

    async def read_passengers(
        self,
        source_file: str | None,
        page: int,
        size: int,
    ) -> WalterPassengerPageDto:
        base_query = select(PersonOrm, BookingOrm).outerjoin(
            BookingOrm, BookingOrm.person_id == PersonOrm.id
        )
        if source_file:
            base_query = base_query.where(PersonOrm.source_file == source_file)

        total = (
            await self.session.execute(
                select(func.count()).select_from(base_query.subquery())
            )
        ).scalar_one()

        rows = (
            await self.session.execute(
                base_query.order_by(PersonOrm.id)
                .offset((page - 1) * size)
                .limit(size)
            )
        ).all()

        total_pages = (total + size - 1) // size if size else 1
        logger.info(f"[WalterRepository] read_passengers | source_file={source_file} page={page} total={total}")

        return WalterPassengerPageDto(
            source_file=source_file,
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
            rows=[_row_to_dict(person, booking) for person, booking in rows],
        )