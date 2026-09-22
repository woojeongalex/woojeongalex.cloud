"""challenge_charts — 악기 연주곡 지원

Revision ID: 20260921_0012
Revises: 20260921_0011
Create Date: 2026-09-21

정답 멜로디를 보컬뿐 아니라 멜로디 악기 스템에서도 뽑을 수 있게 한다.
- vocal_s3_key → melody_s3_key, instrumental_s3_key → backing_s3_key
  (연주곡에서는 "보컬"이 없으므로 역할 이름으로 바꾼다)
- melody_source: 추출 방식(vocal | instrument). 기존 행은 전부 보컬이었다.
- instrument: 연주곡의 멜로디 악기 종류(표시용)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0012"
down_revision: Union[str, Sequence[str], None] = "20260921_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("challenge_charts", "vocal_s3_key", new_column_name="melody_s3_key")
    op.alter_column(
        "challenge_charts", "instrumental_s3_key", new_column_name="backing_s3_key"
    )
    op.add_column(
        "challenge_charts",
        sa.Column(
            "melody_source",
            sa.String(length=20),
            nullable=False,
            server_default="vocal",
        ),
    )
    op.add_column(
        "challenge_charts",
        sa.Column("instrument", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("challenge_charts", "instrument")
    op.drop_column("challenge_charts", "melody_source")
    op.alter_column(
        "challenge_charts", "backing_s3_key", new_column_name="instrumental_s3_key"
    )
    op.alter_column("challenge_charts", "melody_s3_key", new_column_name="vocal_s3_key")
