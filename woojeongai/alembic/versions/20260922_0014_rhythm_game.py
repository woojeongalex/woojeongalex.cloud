"""rhythm_charts, rhythm_plays — 리듬 게임(오투잼식) 채보와 플레이 기록

Revision ID: 20260922_0014
Revises: 20260921_0013
Create Date: 2026-09-22

곡 하나에 4키·7키 × 쉬움·보통·어려움 채보를 원곡에서 자동으로 만든다.
플레이 점수는 서버가 입력 기록으로 다시 계산한 값이며, 랭킹은 채보별로 매긴다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260922_0014"
down_revision: Union[str, Sequence[str], None] = "20260921_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rhythm_charts",
        sa.Column(
            "challenge_id",
            sa.Integer(),
            sa.ForeignKey("music_challenges.id"),
            primary_key=True,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("job_id", sa.String(length=64), nullable=True),
        sa.Column("bpm", sa.Float(), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("sheets", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "rhythm_plays",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "challenge_id",
            sa.Integer(),
            sa.ForeignKey("music_challenges.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("keys", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=10), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=False),
        sa.Column("max_combo", sa.Integer(), nullable=False),
        sa.Column("cool", sa.Integer(), nullable=False),
        sa.Column("good", sa.Integer(), nullable=False),
        sa.Column("bad", sa.Integer(), nullable=False),
        sa.Column("miss", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_rhythm_plays_user_id", "rhythm_plays", ["user_id"])
    # 채보별 랭킹 조회용
    op.create_index(
        "ix_rhythm_plays_sheet_score",
        "rhythm_plays",
        ["challenge_id", "keys", "difficulty", "score"],
    )


def downgrade() -> None:
    op.drop_index("ix_rhythm_plays_sheet_score", table_name="rhythm_plays")
    op.drop_index("ix_rhythm_plays_user_id", table_name="rhythm_plays")
    op.drop_table("rhythm_plays")
    op.drop_table("rhythm_charts")
