"""인증 inbound — DB·SQLAlchemy 예외는 라우터 밖에서 처리."""

import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def db_http_error(exc: SQLAlchemyError, context: str) -> HTTPException:
    logger.exception("%s DB 오류: %s", context, exc)
    return HTTPException(
        status_code=503,
        detail="DB 연결에 실패했습니다. 서버 로그를 확인하세요.",
    )


async def run_with_db_guard(action: Callable[[], Awaitable[T]], context: str) -> T:
    try:
        return await action()
    except SQLAlchemyError as exc:
        raise db_http_error(exc, context) from exc
