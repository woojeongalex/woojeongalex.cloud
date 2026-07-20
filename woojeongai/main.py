# ruff: noqa: E402
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
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

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.db_health_adapter import DbHealthAdapter

try:
    from database import dispose_engine, get_db, init_db
except ModuleNotFoundError:
    from apps.database import dispose_engine, get_db, init_db
from core.matrix.keymaker_api import get_keymaker
from music.adapter.inbound.api import music_router
from friday13th.adapter.inbound.api.v1 import (
    login_router,
    oauth_router,
    signup_router,
    token_router,
)
from titanic.adapter.inbound.api import titanic_router
from silicon_valley.adapter.inbound.api import silicon_valley_router
from star_craft.adapter.inbound.api import star_craft_router

logger = logging.getLogger(__name__)

keymaker = get_keymaker()

# primary 모델 실패(404·429) 시 순서대로 재시도
GEMINI_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
)


class ChatRequest(BaseModel):
    """채팅 요청 본문. 사용자 메시지를 JSON으로 전달합니다."""

    message: str = Field(..., min_length=1, description="사용자 메시지")


class ChatResponse(BaseModel):
    reply: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Neon DB 테이블 초기화 완료")
    except Exception as exc:
        logger.exception(
            "Neon DB init_db 실패 — auth API가 동작하지 않을 수 있습니다: %s", exc
        )
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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signup_router)
app.include_router(login_router)
app.include_router(oauth_router)
app.include_router(token_router)
app.include_router(titanic_router)
app.include_router(silicon_valley_router)
app.include_router(music_router)
app.include_router(star_craft_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "FAST API 메인 페이지 ", "docs": "/docs"}


@dataclass(frozen=True)
class _GeminiErrorRule:
    keywords: tuple[str, ...]
    status_code: int
    detail: str
    retryable: bool


_GEMINI_ERROR_RULES: tuple[_GeminiErrorRule, ...] = (
    _GeminiErrorRule(
        keywords=("429", "quota", "resource_exhausted"),
        status_code=429,
        detail=(
            "Gemini API 할당량을 초과했거나, 이 모델은 현재 요금제에서 사용할 수 없습니다. "
            "Google AI Studio에서 사용량·결제를 확인하거나, "
            "backend/.env 에 GEMINI_MODEL=gemini-2.5-flash 를 넣은 뒤 서버를 재시작해 보세요."
        ),
        retryable=True,
    ),
    _GeminiErrorRule(
        keywords=("404", "not found"),
        status_code=502,
        detail=(
            "지원하지 않는 Gemini 모델입니다. "
            "backend/.env 에 GEMINI_MODEL=gemini-2.5-flash 를 설정해 보세요."
        ),
        retryable=True,
    ),
)


def _match_gemini_rule(exc: Exception) -> _GeminiErrorRule | None:
    msg = str(exc).lower()
    for rule in _GEMINI_ERROR_RULES:
        if any(kw in msg for kw in rule.keywords):
            return rule
    return None


def _gemini_error_to_http(exc: Exception) -> HTTPException:
    rule = _match_gemini_rule(exc)
    if rule:
        return HTTPException(status_code=rule.status_code, detail=rule.detail)
    msg = str(exc)
    short = msg if len(msg) <= 280 else msg[:280] + "…"
    return HTTPException(status_code=502, detail=f"Gemini 호출 실패: {short}")


def _should_try_next_model(exc: Exception) -> bool:
    rule = _match_gemini_rule(exc)
    return rule is not None and rule.retryable


def _generate_gemini_reply(message: str) -> str:
    import google.generativeai as genai

    api_key = keymaker.get_gemini_api_key()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )

    genai.configure(api_key=api_key)
    primary = keymaker.get_gemini_model_name()
    model_ids = [primary] + [m for m in GEMINI_FALLBACK_MODELS if m != primary]

    last_exc: Exception | None = None
    for model_id in model_ids:
        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content(message)
            try:
                text = (response.text or "").strip()
            except ValueError as e:
                feedback = getattr(response, "prompt_feedback", None)
                raise HTTPException(
                    status_code=400,
                    detail=f"응답 텍스트를 읽을 수 없습니다: {e!s}. prompt_feedback={feedback}",
                ) from e

            if not text:
                reason = None
                if getattr(response, "candidates", None):
                    c0 = response.candidates[0]
                    reason = getattr(c0, "finish_reason", None)
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "모델이 비어 있는 응답을 반환했습니다."
                        + (f" (finish_reason={reason})" if reason else "")
                    ),
                )
            return text
        except HTTPException:
            raise
        except Exception as e:
            last_exc = e
            if _should_try_next_model(e) and model_id != model_ids[-1]:
                continue
            raise _gemini_error_to_http(e) from e

    if last_exc is not None:
        raise _gemini_error_to_http(last_exc)
    raise HTTPException(status_code=502, detail="Gemini 호출에 실패했습니다.")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    JSON 본문 `{"message": "..."}` 를 받아 Gemini 답변 문자열을 반환합니다.
    """
    if not keymaker.is_gemini_ready():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )

    try:
        reply = _generate_gemini_reply(req.message)
    except HTTPException:
        raise
    except Exception as e:
        raise _gemini_error_to_http(e) from e

    return ChatResponse(reply=reply)


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
