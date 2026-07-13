"""stadium · team · schedule · player 테이블 생성

Revision ID: 20260713_0002
Revises: 20260604_0001
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0002"
down_revision: Union[str, Sequence[str], None] = "20260604_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stadium",
        sa.Column("stadium_id", sa.String(length=10), nullable=False),
        sa.Column("statdium_name", sa.String(length=40), nullable=True),
        sa.Column("hometeam_id", sa.String(length=10), nullable=True),
        sa.Column("seat_count", sa.Integer(), nullable=True),
        sa.Column("address", sa.String(length=60), nullable=True),
        sa.Column("ddd", sa.String(length=10), nullable=True),
        sa.Column("tel", sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint("stadium_id"),
    )

    op.create_table(
        "team",
        sa.Column("team_id", sa.String(length=10), nullable=False),
        sa.Column("region_name", sa.String(length=10), nullable=True),
        sa.Column("team_name", sa.String(length=40), nullable=True),
        sa.Column("e_team_name", sa.String(length=50), nullable=True),
        sa.Column("nickname", sa.String(length=10), nullable=True),
        sa.Column("orig_yyyy", sa.String(length=10), nullable=True),
        sa.Column("zip_code1", sa.String(length=10), nullable=True),
        sa.Column("zip_code2", sa.String(length=10), nullable=True),
        sa.Column("address", sa.String(length=80), nullable=True),
        sa.Column("ddd", sa.String(length=10), nullable=True),
        sa.Column("tel", sa.String(length=10), nullable=True),
        sa.Column("fax", sa.String(length=10), nullable=True),
        sa.Column("homepage", sa.String(length=50), nullable=True),
        sa.Column("owner", sa.String(length=10), nullable=True),
        sa.Column("stadium_id", sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(["stadium_id"], ["stadium.stadium_id"]),
        sa.PrimaryKeyConstraint("team_id"),
    )
    op.create_index("ix_team_stadium_id", "team", ["stadium_id"])

    # schedule: 원본 ERD의 PK는 sche_date 단독이지만, 이 경우 하루 한 경기만
    # 저장 가능해진다. 프로젝트 기존 컨벤션(surrogate integer PK)을 따라
    # schedule_id를 PK로 추가하고 sche_date는 일반 컬럼 + 인덱스로 둔다.
    op.create_table(
        "schedule",
        sa.Column("schedule_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sche_date", sa.String(length=10), nullable=False),
        sa.Column("stadium_id", sa.String(length=10), nullable=True),
        sa.Column("gubun", sa.String(length=10), nullable=True),
        sa.Column("hometeam_id", sa.String(length=10), nullable=True),
        sa.Column("awayteam_id", sa.String(length=10), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["stadium_id"], ["stadium.stadium_id"]),
        sa.ForeignKeyConstraint(["hometeam_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["awayteam_id"], ["team.team_id"]),
        sa.PrimaryKeyConstraint("schedule_id"),
    )
    op.create_index("ix_schedule_sche_date", "schedule", ["sche_date"])
    op.create_index("ix_schedule_stadium_id", "schedule", ["stadium_id"])
    op.create_index("ix_schedule_hometeam_id", "schedule", ["hometeam_id"])
    op.create_index("ix_schedule_awayteam_id", "schedule", ["awayteam_id"])

    op.create_table(
        "player",
        sa.Column("player_id", sa.String(length=10), nullable=False),
        sa.Column("player_name", sa.String(length=20), nullable=True),
        sa.Column("e_player_name", sa.String(length=40), nullable=True),
        sa.Column("nickname", sa.String(length=30), nullable=True),
        sa.Column("join_yyyy", sa.String(length=10), nullable=True),
        sa.Column("position", sa.String(length=10), nullable=True),
        sa.Column("back_no", sa.Integer(), nullable=True),
        sa.Column("nation", sa.String(length=20), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("solar", sa.String(length=10), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
        sa.PrimaryKeyConstraint("player_id"),
    )
    op.create_index("ix_player_team_id", "player", ["team_id"])


def downgrade() -> None:
    op.drop_index("ix_player_team_id", table_name="player")
    op.drop_table("player")

    op.drop_index("ix_schedule_awayteam_id", table_name="schedule")
    op.drop_index("ix_schedule_hometeam_id", table_name="schedule")
    op.drop_index("ix_schedule_stadium_id", table_name="schedule")
    op.drop_index("ix_schedule_sche_date", table_name="schedule")
    op.drop_table("schedule")

    op.drop_index("ix_team_stadium_id", table_name="team")
    op.drop_table("team")

    op.drop_table("stadium")
