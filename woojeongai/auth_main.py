# ruff: noqa: E402
"""Auth Gateway 엔트리포인트 — auth.woojeongalex.cloud (port 9000).

uvicorn auth_main:app --host 0.0.0.0 --port 9000
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent
_APPS_DIR = _CURRENT_DIR / "apps"
for _path in (_CURRENT_DIR, _APPS_DIR):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from logging_setup import configure_logging

configure_logging()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.auth.router import auth_router

try:
    from database import dispose_engine, init_db
except ModuleNotFoundError:
    from apps.database import dispose_engine, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(
    title="Woojeongalex Auth Gateway",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://woojeongalex.cloud",
        "https://www.woojeongalex.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}
