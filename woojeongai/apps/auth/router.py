"""Auth Gateway 라우터 — RS256 JWT 발급 전용."""

from __future__ import annotations

import base64
import os

import jwt as pyjwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode

try:
    from database import get_db
except ModuleNotFoundError:
    from apps.database import get_db

from apps.auth.schemas import (
    AccessTokenResponse,
    JwksResponse,
    RefreshRequest,
)
from apps.auth.services import (
    find_or_create_user,
    google_authorize_url,
    google_fetch_user,
    issue_token_pair,
    kakao_authorize_url,
    kakao_fetch_user,
    naver_authorize_url,
    naver_fetch_user,
)
from core.dependencies import get_current_user
from core.security import create_access_token, verify_token
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)

auth_router = APIRouter(tags=["auth-gateway"])

_FRONTEND_URL = os.getenv("FRONTEND_URL", "https://woojeongalex.cloud")


# ── 리다이렉트 헬퍼 ──────────────────────────────────────────────────────────


def _ok_redirect(access_token: str, refresh_token: str) -> RedirectResponse:
    qs = urlencode({"access_token": access_token, "refresh_token": refresh_token})
    return RedirectResponse(
        f"{_FRONTEND_URL}/auth/social-callback?{qs}", status_code=302
    )


def _err_redirect(msg: str) -> RedirectResponse:
    qs = urlencode({"error": msg})
    return RedirectResponse(
        f"{_FRONTEND_URL}/auth/social-callback?{qs}", status_code=302
    )


# ── JWKS ─────────────────────────────────────────────────────────────────────


@auth_router.get("/.well-known/jwks.json", response_model=JwksResponse)
def jwks() -> JwksResponse:
    """공개키를 JWK 형식으로 반환 — 백엔드/외부 검증자용."""
    raw = os.getenv("JWT_PUBLIC_KEY", "")
    if not raw:
        raise HTTPException(status_code=503, detail="JWT_PUBLIC_KEY not configured")
    pem = base64.b64decode(raw) if not raw.startswith("-----") else raw.encode()
    pub: RSAPublicKey = serialization.load_pem_public_key(pem)  # type: ignore[assignment]
    pub_numbers = (
        pub.public_key().public_numbers()
        if hasattr(pub, "public_key")
        else pub.public_numbers()
    )

    def _int_to_b64(n: int) -> str:
        length = (n.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()

    return JwksResponse(
        keys=[
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": "woojeongalex-key-1",
                "n": _int_to_b64(pub_numbers.n),
                "e": _int_to_b64(pub_numbers.e),
            }
        ]
    )


# ── 토큰 갱신 / 로그아웃 / Me ────────────────────────────────────────────────


@auth_router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(body: RefreshRequest) -> AccessTokenResponse:
    try:
        payload = verify_token(body.refresh_token, aud="woojeongalex-refresh")
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다.")
    except pyjwt.PyJWTError:
        raise HTTPException(
            status_code=401, detail="유효하지 않은 리프레시 토큰입니다."
        )

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="리프레시 토큰이 아닙니다.")

    username = payload.get("sub", "")
    jti = payload.get("jti", "")
    role = payload.get("role", "user")

    repo = RedisSessionRepository()
    if not repo.validate_refresh(username, jti):
        # 재사용 감지 → 세션 전체 폐기
        repo.revoke(username, jti)
        raise HTTPException(
            status_code=401, detail="토큰 재사용 감지 — 세션이 폐기되었습니다."
        )

    new_token, new_jti, ttl = create_access_token(username, role)
    repo.save_access(new_jti, username, ttl)
    return AccessTokenResponse(access_token=new_token)


@auth_router.post("/logout")
async def logout(payload: dict = Depends(get_current_user)) -> dict:
    username = payload["sub"]
    jti = payload.get("jti", "")
    RedisSessionRepository().revoke(username, jti)
    return {"ok": True, "message": "로그아웃되었습니다."}


@auth_router.get("/me")
async def me(payload: dict = Depends(get_current_user)) -> dict:
    return {"username": payload["sub"], "role": payload.get("role", "user")}


# ── OAuth 콜백 — Naver ────────────────────────────────────────────────────────


@auth_router.get("/naver")
def naver_login() -> RedirectResponse:
    return RedirectResponse(naver_authorize_url(), status_code=302)


@auth_router.get("/naver/callback")
async def naver_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return _err_redirect(f"naver_denied:{error or 'no_code'}")
    try:
        info = await naver_fetch_user(code, state or "")
        if not info:
            return _err_redirect("naver_profile_failed")
        user = await find_or_create_user(db, **info)
        at, rt = issue_token_pair(user)
        return _ok_redirect(at, rt)
    except Exception:
        return _err_redirect("naver_error")


# ── OAuth 콜백 — Kakao ────────────────────────────────────────────────────────


@auth_router.get("/kakao")
def kakao_login() -> RedirectResponse:
    return RedirectResponse(kakao_authorize_url(), status_code=302)


@auth_router.get("/kakao/callback")
async def kakao_callback(
    code: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return _err_redirect(f"kakao_denied:{error or 'no_code'}")
    try:
        info = await kakao_fetch_user(code)
        if not info:
            return _err_redirect("kakao_profile_failed")
        user = await find_or_create_user(db, **info)
        at, rt = issue_token_pair(user)
        return _ok_redirect(at, rt)
    except Exception:
        return _err_redirect("kakao_error")


# ── OAuth 콜백 — Google ───────────────────────────────────────────────────────


@auth_router.get("/google")
def google_login() -> RedirectResponse:
    return RedirectResponse(google_authorize_url(), status_code=302)


@auth_router.get("/google/callback")
async def google_callback(
    code: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return _err_redirect(f"google_denied:{error or 'no_code'}")
    try:
        info = await google_fetch_user(code)
        if not info:
            return _err_redirect("google_profile_failed")
        user = await find_or_create_user(db, **info)
        at, rt = issue_token_pair(user)
        return _ok_redirect(at, rt)
    except Exception:
        return _err_redirect("google_error")
