"""레거시 import 호환용 database 모듈.

기존 `from database import ...` 코드를 유지하기 위해
`core.database`를 재노출합니다.
"""

from core.database import dispose_engine, get_db, init_db

__all__ = ["dispose_engine", "get_db", "init_db"]
