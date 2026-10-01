# ruff: noqa: E402
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_CURRENT_DIR = Path(__file__).resolve().parent
_APPS_DIR = _CURRENT_DIR / "apps"
for _path in (_CURRENT_DIR, _APPS_DIR):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from logging_setup import configure_logging

configure_logging()

from fastapi import Depends, FastAPI
from core.dependencies import RoleChecker
from apps.auth.rbac import Role

require_admin = RoleChecker(Role.ADMIN)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.db_health_adapter import DbHealthAdapter

try:
    from database import dispose_engine, get_db
except ModuleNotFoundError:
    from apps.database import dispose_engine, get_db
from core.matrix.keymaker_api import get_keymaker
from music.adapter.inbound.api import music_router
from friday13th.adapter.inbound.api.v1 import (
    login_router,
    oauth_router,
    signup_router,
    token_router,
)
from music_challenge.adapter.inbound.api import music_challenge_router
from ocr.adapter.inbound.api import ocr_router
import music_challenge.adapter.outbound.orm.music_challenge_orm  # noqa: F401 — Alembic autogenerate

logger = logging.getLogger(__name__)

keymaker = get_keymaker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.matrix.database_manager import init_engine

    init_engine()
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(title="Woojeongalex Main Page", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://woojeongalex.cloud",
        "https://www.woojeongalex.cloud",
        "https://app.woojeongalex.cloud",
        "http://app.woojeongalex.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signup_router)
app.include_router(login_router)
app.include_router(oauth_router)
app.include_router(token_router)
app.include_router(music_router)
app.include_router(music_challenge_router)
app.include_router(ocr_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "FAST API 메인 페이지 ", "docs": "/docs"}


@app.get("/db-check")
async def check_db(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return await DbHealthAdapter.neon_time_check(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
