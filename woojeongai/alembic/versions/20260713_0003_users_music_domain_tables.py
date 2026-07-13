"""users · music 도메인 테이블 생성 (ERD 기반)

Revision ID: 20260713_0003
Revises: 20260713_0002
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0003"
down_revision: Union[str, Sequence[str], None] = "20260713_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="user"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_nickname", "users", ["nickname"])

    # catalog_songs: ERD의 신규 테이블. 현재 곡 카탈로그는 domain/vocal_bard_searcher_catalog.py
    # 에 인메모리로만 존재하고 어떤 FK도 여기를 참조하지 않는다. 향후 DB 이관용 빈 테이블만 생성.
    op.create_table(
        "catalog_songs",
        sa.Column("catalog_song_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=True),
        sa.Column("artist", sa.String(length=256), nullable=True),
        sa.Column("bpm", sa.Integer(), nullable=True),
        sa.Column("song_key", sa.String(length=64), nullable=True),
        sa.Column("range_label", sa.String(length=128), nullable=True),
        sa.Column("mr_track_name", sa.String(length=256), nullable=True),
        sa.Column("mr_description", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("catalog_song_id"),
    )

    op.create_table(
        "sing_evaluations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sing_evaluations_user_id", "sing_evaluations", ["user_id"])

    op.create_table(
        "speech_evaluations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_speech_evaluations_user_id", "speech_evaluations", ["user_id"])

    op.create_table(
        "instrument_evaluations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_instrument_evaluations_user_id", "instrument_evaluations", ["user_id"])

    op.create_table(
        "song_mr_search_lists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("search_query", sa.String(length=256), nullable=False),
        sa.Column("catalog_song_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("artist", sa.String(length=256), nullable=False),
        sa.Column("bpm", sa.Integer(), nullable=False),
        sa.Column("song_key", sa.String(length=64), nullable=False),
        sa.Column("range_label", sa.String(length=128), nullable=False),
        sa.Column("mr_track_name", sa.String(length=256), nullable=False),
        sa.Column("mr_description", sa.String(length=512), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_song_mr_search_lists_search_query", "song_mr_search_lists", ["search_query"])
    op.create_index("ix_song_mr_search_lists_catalog_song_id", "song_mr_search_lists", ["catalog_song_id"])

    op.create_table(
        "user_vocal_recordings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("catalog_song_id", sa.String(length=64), nullable=True),
        sa.Column("mr_search_list_id", sa.Integer(), nullable=True),
        sa.Column("sing_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("input_source", sa.String(length=16), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("duration_sec", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("storage_uri", sa.String(length=1024), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["mr_search_list_id"], ["song_mr_search_lists.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["sing_evaluation_id"], ["sing_evaluations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sing_evaluation_id"),
    )
    op.create_index("ix_user_vocal_recordings_user_id", "user_vocal_recordings", ["user_id"])
    op.create_index(
        "ix_user_vocal_recordings_catalog_song_id", "user_vocal_recordings", ["catalog_song_id"]
    )
    op.create_index(
        "ix_user_vocal_recordings_mr_search_list_id", "user_vocal_recordings", ["mr_search_list_id"]
    )
    op.create_index(
        "ix_user_vocal_recordings_sing_evaluation_id", "user_vocal_recordings", ["sing_evaluation_id"]
    )

    op.create_table(
        "ai_vocal_analyses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_vocal_recording_id", sa.Integer(), nullable=False),
        sa.Column("analysis_engine", sa.String(length=32), nullable=False),
        sa.Column("pitch_score", sa.Integer(), nullable=False),
        sa.Column("rhythm_score", sa.Integer(), nullable=False),
        sa.Column("vocal_grade", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.String(length=2048), nullable=False),
        sa.Column(
            "analyzed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_vocal_recording_id"], ["user_vocal_recordings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_vocal_recording_id"),
    )
    op.create_index(
        "ix_ai_vocal_analyses_user_vocal_recording_id", "ai_vocal_analyses", ["user_vocal_recording_id"]
    )

    op.create_table(
        "vocal_recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sing_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("ai_vocal_analysis_id", sa.Integer(), nullable=False),
        sa.Column("vocalization_pattern", sa.String(length=1024), nullable=False),
        sa.Column("recommended_genres", sa.JSON(), nullable=False),
        sa.Column("recommended_songs", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["sing_evaluation_id"], ["sing_evaluations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["ai_vocal_analysis_id"], ["ai_vocal_analyses.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vocal_recommendations_sing_evaluation_id", "vocal_recommendations", ["sing_evaluation_id"]
    )
    op.create_index(
        "ix_vocal_recommendations_ai_vocal_analysis_id",
        "vocal_recommendations",
        ["ai_vocal_analysis_id"],
    )

    op.create_table(
        "instrument_recordings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("instrument_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("instrument_id", sa.String(length=32), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("duration_sec", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["instrument_evaluation_id"], ["instrument_evaluations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_evaluation_id"),
    )
    op.create_index("ix_instrument_recordings_user_id", "instrument_recordings", ["user_id"])
    op.create_index(
        "ix_instrument_recordings_instrument_evaluation_id",
        "instrument_recordings",
        ["instrument_evaluation_id"],
    )

    op.create_table(
        "instrument_tuning_analyses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instrument_recording_id", sa.Integer(), nullable=False),
        sa.Column(
            "analysis_engine", sa.String(length=64), nullable=False, server_default="client_demo"
        ),
        sa.Column("tuning_accuracy", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pitch_deviation_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary", sa.String(length=2048), nullable=False, server_default=""),
        sa.Column("string_readings", sa.JSON(), nullable=False),
        sa.Column(
            "analyzed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["instrument_recording_id"], ["instrument_recordings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_recording_id"),
    )
    op.create_index(
        "ix_instrument_tuning_analyses_instrument_recording_id",
        "instrument_tuning_analyses",
        ["instrument_recording_id"],
    )

    op.create_table(
        "speech_recordings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("speech_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.String(length=64), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("duration_sec", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["speech_evaluation_id"], ["speech_evaluations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("speech_evaluation_id"),
    )
    op.create_index("ix_speech_recordings_user_id", "speech_recordings", ["user_id"])
    op.create_index("ix_speech_recordings_topic_id", "speech_recordings", ["topic_id"])
    op.create_index(
        "ix_speech_recordings_speech_evaluation_id", "speech_recordings", ["speech_evaluation_id"]
    )

    op.create_table(
        "speech_feedback_analyses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("speech_recording_id", sa.Integer(), nullable=False),
        sa.Column(
            "analysis_engine", sa.String(length=64), nullable=False, server_default="client_demo"
        ),
        sa.Column("clarity_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pace_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tone_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary", sa.String(length=2048), nullable=False, server_default=""),
        sa.Column("feedback_points", sa.JSON(), nullable=False),
        sa.Column(
            "analyzed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["speech_recording_id"], ["speech_recordings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("speech_recording_id"),
    )
    op.create_index(
        "ix_speech_feedback_analyses_speech_recording_id",
        "speech_feedback_analyses",
        ["speech_recording_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_speech_feedback_analyses_speech_recording_id", table_name="speech_feedback_analyses"
    )
    op.drop_table("speech_feedback_analyses")

    op.drop_index("ix_speech_recordings_speech_evaluation_id", table_name="speech_recordings")
    op.drop_index("ix_speech_recordings_topic_id", table_name="speech_recordings")
    op.drop_index("ix_speech_recordings_user_id", table_name="speech_recordings")
    op.drop_table("speech_recordings")

    op.drop_index(
        "ix_instrument_tuning_analyses_instrument_recording_id",
        table_name="instrument_tuning_analyses",
    )
    op.drop_table("instrument_tuning_analyses")

    op.drop_index(
        "ix_instrument_recordings_instrument_evaluation_id", table_name="instrument_recordings"
    )
    op.drop_index("ix_instrument_recordings_user_id", table_name="instrument_recordings")
    op.drop_table("instrument_recordings")

    op.drop_index(
        "ix_vocal_recommendations_ai_vocal_analysis_id", table_name="vocal_recommendations"
    )
    op.drop_index(
        "ix_vocal_recommendations_sing_evaluation_id", table_name="vocal_recommendations"
    )
    op.drop_table("vocal_recommendations")

    op.drop_index(
        "ix_ai_vocal_analyses_user_vocal_recording_id", table_name="ai_vocal_analyses"
    )
    op.drop_table("ai_vocal_analyses")

    op.drop_index(
        "ix_user_vocal_recordings_sing_evaluation_id", table_name="user_vocal_recordings"
    )
    op.drop_index(
        "ix_user_vocal_recordings_mr_search_list_id", table_name="user_vocal_recordings"
    )
    op.drop_index(
        "ix_user_vocal_recordings_catalog_song_id", table_name="user_vocal_recordings"
    )
    op.drop_index("ix_user_vocal_recordings_user_id", table_name="user_vocal_recordings")
    op.drop_table("user_vocal_recordings")

    op.drop_index(
        "ix_song_mr_search_lists_catalog_song_id", table_name="song_mr_search_lists"
    )
    op.drop_index("ix_song_mr_search_lists_search_query", table_name="song_mr_search_lists")
    op.drop_table("song_mr_search_lists")

    op.drop_index("ix_instrument_evaluations_user_id", table_name="instrument_evaluations")
    op.drop_table("instrument_evaluations")

    op.drop_index("ix_speech_evaluations_user_id", table_name="speech_evaluations")
    op.drop_table("speech_evaluations")

    op.drop_index("ix_sing_evaluations_user_id", table_name="sing_evaluations")
    op.drop_table("sing_evaluations")

    op.drop_table("catalog_songs")

    op.drop_index("ix_users_nickname", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
