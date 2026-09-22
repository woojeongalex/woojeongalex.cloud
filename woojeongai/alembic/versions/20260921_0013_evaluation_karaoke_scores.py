"""submission_evaluations — 노래방·연주 서버 채점 결과

Revision ID: 20260921_0013
Revises: 20260921_0012
Create Date: 2026-09-21

노래방·연주 모드로 제출하면 서버가 녹음을 정답 음표와 맞춰 다시 채점한다.
화면 점수는 조작할 수 있으므로 랭킹은 이 값만 쓴다. 일반 제출이면 비어 있다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0013"
down_revision: Union[str, Sequence[str], None] = "20260921_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "submission_evaluations",
        sa.Column("karaoke_score", sa.Integer(), nullable=True),
    )
    op.add_column(
        "submission_evaluations",
        sa.Column("karaoke_pitch_accuracy", sa.Integer(), nullable=True),
    )
    op.add_column(
        "submission_evaluations",
        sa.Column("karaoke_timing_accuracy", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_submission_evaluations_karaoke_score",
        "submission_evaluations",
        ["karaoke_score"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_submission_evaluations_karaoke_score", table_name="submission_evaluations"
    )
    op.drop_column("submission_evaluations", "karaoke_timing_accuracy")
    op.drop_column("submission_evaluations", "karaoke_pitch_accuracy")
    op.drop_column("submission_evaluations", "karaoke_score")
