"""music_challenge 도메인 테이블 생성

Revision ID: 20260824_0008
Revises: 20260722_0007
Create Date: 2026-08-24

apps/music_challenge/adapter/outbound/orm/music_challenge_orm.py 의 세 모델을
그대로 옮긴 것이다. DB에 붙지 못하는 상태에서 작성했으므로 autogenerate 가
아니라 모델을 보고 수기로 작성했다.

created_at 은 ORM 이 `default=datetime.utcnow` 로 파이썬 쪽에서 채우므로
server_default 를 두지 않는다(= SQLModel 이 create_all 로 만들 스키마와 동일).

FK 컬럼 인덱스는 ORM 에도 index=True 로 함께 선언해 두 쪽이 어긋나지 않게 했다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260824_0008"
down_revision: Union[str, Sequence[str], None] = "20260722_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "music_challenges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("music_s3_key", sa.String(length=500), nullable=False),
        sa.Column("challenge_type", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "challenge_submissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(length=10), nullable=False),
        sa.Column("s3_key", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["challenge_id"], ["music_challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_challenge_submissions_challenge_id",
        "challenge_submissions",
        ["challenge_id"],
    )

    op.create_table(
        "submission_evaluations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("next_challenge_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["challenge_submissions.id"]),
        sa.ForeignKeyConstraint(["next_challenge_id"], ["music_challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_submission_evaluations_submission_id",
        "submission_evaluations",
        ["submission_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_submission_evaluations_submission_id", table_name="submission_evaluations"
    )
    op.drop_table("submission_evaluations")

    op.drop_index(
        "ix_challenge_submissions_challenge_id", table_name="challenge_submissions"
    )
    op.drop_table("challenge_submissions")

    op.drop_table("music_challenges")
