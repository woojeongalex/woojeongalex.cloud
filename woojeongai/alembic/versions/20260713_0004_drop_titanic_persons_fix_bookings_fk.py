"""drop dead titanic_persons; repoint titanic_bookings fk to titanic_passengers

titanic_persons/titanic_bookings were created by 20260604_0001 for the old
SQLModel Person/Booking entities. Those entities were later replaced by
PersonOrm/BookingOrm (core.matrix.theone_base.Base), which target
titanic_passengers/titanic_bookings instead. Since create_all() only
creates missing tables and never alters existing ones, titanic_bookings
kept its original FK to titanic_persons even after the code moved to
titanic_passengers — leaving a live FK that doesn't match what the app
actually inserts into. titanic_persons itself is unreferenced by any
current code and empty.

Revision ID: 20260713_0004
Revises: 20260713_0003
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0004"
down_revision: Union[str, Sequence[str], None] = "20260713_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("titanic_bookings_person_id_fkey", "titanic_bookings", type_="foreignkey")
    op.create_foreign_key(
        "titanic_bookings_person_id_fkey",
        "titanic_bookings",
        "titanic_passengers",
        ["person_id"],
        ["id"],
    )

    op.drop_index("ix_titanic_persons_passenger_id", table_name="titanic_persons")
    op.drop_index("ix_titanic_persons_source_file", table_name="titanic_persons")
    op.drop_table("titanic_persons")


def downgrade() -> None:
    op.create_table(
        "titanic_persons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("passenger_id", sa.String(length=32), nullable=False),
        sa.Column("survived", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("age", sa.String(length=32), nullable=False),
        sa.Column("sib_sp", sa.String(length=8), nullable=False),
        sa.Column("parch", sa.String(length=8), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_titanic_persons_source_file", "titanic_persons", ["source_file"])
    op.create_index("ix_titanic_persons_passenger_id", "titanic_persons", ["passenger_id"])

    op.drop_constraint("titanic_bookings_person_id_fkey", "titanic_bookings", type_="foreignkey")
    op.create_foreign_key(
        "titanic_bookings_person_id_fkey",
        "titanic_bookings",
        "titanic_persons",
        ["person_id"],
        ["id"],
    )
