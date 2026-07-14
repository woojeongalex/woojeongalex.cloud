"""add pgvector embedding column to catalog_songs for RAG semantic search

Enables the pgvector extension (not yet enabled on this DB) and adds a
4096-dim vector column matching EXAONE-3.5-7.8B-Instruct-AWQ's hidden_size,
used as the embedding model via a local vLLM pooling server.

Revision ID: 20260714_0005
Revises: 20260713_0004
Create Date: 2026-07-14

"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260714_0005"
down_revision: Union[str, Sequence[str], None] = "20260713_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("ALTER TABLE catalog_songs ADD COLUMN embedding vector(4096)")


def downgrade() -> None:
    op.execute("ALTER TABLE catalog_songs DROP COLUMN embedding")
