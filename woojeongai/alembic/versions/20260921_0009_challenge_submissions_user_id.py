"""challenge_submissions 에 user_id 추가

Revision ID: 20260921_0009
Revises: 20260824_0008
Create Date: 2026-09-21

제출물이 누구 것인지 DB가 몰라서 내 기록·랭킹·개인화 추천이 전부 막혀 있었다.
비로그인 참여를 계속 허용하므로 nullable 이며, 값은 서버가 JWT 에서 도출한
것만 들어간다(클라이언트가 보낸 id 는 신뢰하지 않는다).

ORM(ChallengeSubmissionModel.user_id)과 동일하게 ondelete 없이 평범한 FK 로
둔다 — 스키마와 모델이 어긋나면 autogenerate 가 매번 오탐을 낸다.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260921_0009"
down_revision: Union[str, Sequence[str], None] = "20260824_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "challenge_submissions",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_challenge_submissions_user_id",
        "challenge_submissions",
        ["user_id"],
    )
    op.create_foreign_key(
        "fk_challenge_submissions_user_id_users",
        "challenge_submissions",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_challenge_submissions_user_id_users",
        "challenge_submissions",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_challenge_submissions_user_id",
        table_name="challenge_submissions",
    )
    op.drop_column("challenge_submissions", "user_id")
