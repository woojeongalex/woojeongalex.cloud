"""challenge_charts — 노래방 화면용 악보

Revision ID: 20260921_0011
Revises: 20260921_0010
Create Date: 2026-09-21

챌린지마다 정답 멜로디(보컬 스템에서 추출한 음표), 가사 타이밍, 스템 위치를
담는다. 수백 개의 음표를 목록 조회마다 싣지 않도록 music_challenges 와 분리했다.

주의: 이 파일은 autogenerate 결과에서 challenge_charts 부분만 남긴 것이다.
autogenerate 는 env.py 가 모델을 import 하지 않는 다른 앱의 테이블들을
삭제 대상으로 잡으므로 결과를 그대로 쓰면 안 된다.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260921_0011"
down_revision: str | Sequence[str] | None = "20260921_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "challenge_charts",
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.JSON(), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("vocal_s3_key", sa.String(length=500), nullable=True),
        sa.Column("instrumental_s3_key", sa.String(length=500), nullable=True),
        sa.Column("lyric_lines", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["music_challenges.id"],
            name="fk_challenge_charts_challenge_id_music_challenges",
        ),
        sa.PrimaryKeyConstraint("challenge_id"),
    )


def downgrade() -> None:
    op.drop_table("challenge_charts")
