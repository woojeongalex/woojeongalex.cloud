"""Neon DB — `core.matrix.database_manager` re-export."""

from core.matrix.database_manager import (
    create_all_tables as init_db,
    dispose_engine,
    get_db,
)

__all__ = [
    "dispose_engine",
    "get_db",
    "init_db",
]
