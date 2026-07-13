"""Alembic env — SQLModel metadata + Neon DATABASE_URL."""

from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_APPS_DIR = _BACKEND_DIR / "apps"
for _path in (_BACKEND_DIR, _APPS_DIR):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

load_dotenv(_BACKEND_DIR / ".env")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


_ALEMBIC_SYNC_TO_ASYNC_PREFIX: dict[str, str] = {
    "postgresql://": "postgresql+asyncpg://",
    "postgres://": "postgresql+asyncpg://",
    "postgresql+psycopg://": "postgresql+asyncpg://",
}

_ALEMBIC_ALREADY_ASYNC = ("postgresql+asyncpg://",)


def _alembic_database_url() -> str:
    """온라인(async) 마이그레이션용 URL."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL이 설정되지 않았습니다. backend/.env를 확인하세요.")
    if url.startswith(_ALEMBIC_ALREADY_ASYNC):
        return url
    for sync_prefix, async_prefix in _ALEMBIC_SYNC_TO_ASYNC_PREFIX.items():
        if url.startswith(sync_prefix):
            return async_prefix + url[len(sync_prefix):]
    return url


def _import_models() -> None:
    import friday13th.adapter.outbound.orm.user_model  # noqa: F401
    import titanic.adapter.outbound.orm.passenger_orm  # noqa: F401
    import titanic.adapter.outbound.orm.booking_orm  # noqa: F401


def run_migrations_offline() -> None:
    _import_models()
    url = _alembic_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    _import_models()
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _alembic_database_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
