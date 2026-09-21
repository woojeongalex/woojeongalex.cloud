"""submission_evaluations 에 신호 분석 지표 추가

Revision ID: 20260921_0010
Revises: 20260921_0009
Create Date: 2026-09-21

Gemini 단독 채점은 동일한 파일에 0~70점으로 흔들렸다(실측). librosa 로
음정 안정성·박자 일관성을 결정적으로 측정해 함께 저장하고, 화면에서 종합
점수와 분리해 보여준다.

영상 제출처럼 디코딩할 수 없는 입력은 지표가 없으므로 전부 nullable.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0010"
down_revision: Union[str, Sequence[str], None] = "20260921_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "submission_evaluations",
        sa.Column("pitch_score", sa.Integer(), nullable=True),
    )
    op.add_column(
        "submission_evaluations",
        sa.Column("rhythm_score", sa.Integer(), nullable=True),
    )
    op.add_column(
        "submission_evaluations",
        sa.Column("tempo", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("submission_evaluations", "tempo")
    op.drop_column("submission_evaluations", "rhythm_score")
    op.drop_column("submission_evaluations", "pitch_score")
