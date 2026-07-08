from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
# [변경 1] 함수형 declarative_base 대신 클래스형 DeclarativeBase 임포트
from sqlalchemy.orm import DeclarativeBase

from core.config import DATABASE_URL


# [변경 1] 2.0 표준: 클래스 상속 방식으로 Base 선언 (타입 힌트 및 IDE 자동완성 완벽 지원)
class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> None:
    global engine, async_session_factory
    if not DATABASE_URL:
        return
        
    # 이미 초기화되었다면 중복 생성을 방지 (레이스 컨디션 완화)
    if engine is not None:
        return

    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    
    # [변경 2] async_sessionmaker는 class_=AsyncSession을 기본으로 내장하므로 생략 가능
    # [변경 3] 2.0에서 완전히 제거(Deprecated & Removed)된 autocommit=False 옵션 삭제
    async_session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        init_engine()
        
    if async_session_factory is None:
        raise RuntimeError("데이터베이스 엔진이 초기화되지 않았습니다.")

    # 원본의 안전한 비동기 컨텍스트 매니저 패턴 유지
    async with async_session_factory() as session:
        yield session


async def create_all_tables() -> None:
    import logging
    from sqlalchemy import text

    log = logging.getLogger("backend_main")

    if engine is None:
        init_engine()

    if engine is not None:
        from sqlmodel import SQLModel
        from core.matrix.theone_base import Base as TheOneBase

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(TheOneBase.metadata.create_all)
            await conn.run_sync(SQLModel.metadata.create_all)

        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
            )
            tables = [r[0] for r in result.fetchall()]
            log.info("Neon DB 테이블 목록 (%d개): %s", len(tables), ", ".join(tables))


async def dispose_engine() -> None:
    global engine, async_session_factory
    if engine is not None:
        await engine.dispose()
    engine = None
    async_session_factory = None