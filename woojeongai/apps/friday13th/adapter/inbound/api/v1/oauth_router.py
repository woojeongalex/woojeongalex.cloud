"""Social OAuth — Naver / Kakao / Google.

GET /auth/{provider}          → provider OAuth 로그인 URL 리다이렉트
GET /auth/{provider}/callback → 토큰 교환 → 유저 조회/생성 → JWT 발급 → 프론트 리다이렉트
"""

from __future__ import annotations

import asyncio
import os
import secrets
from urllib.parse import urlencode

import requests as http
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from database import get_db
except ModuleNotFoundError:
    from apps.database import get_db

from core.jwt.jwt_util import create_access_token, create_refresh_token
from friday13th.adapter.outbound.orm.user_model import UserEntity, hash_password
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)

oauth_router = APIRouter(tags=["oauth"])

_FRONTEND_URL = os.getenv("FRONTEND_URL", "https://woojeongalex.cloud")


# ── 공통 헬퍼 ────────────────────────────────────────────────────────────────


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


async def _find_or_create(
    db: AsyncSession,
    username: str,
    nickname: str,
    email: str,
) -> UserEntity:
    row = (
        await db.execute(select(UserEntity).where(UserEntity.username == username))
    ).scalar_one_or_none()
    if row is None:
        row = UserEntity(
            username=username,
            nickname=nickname or username,
            email=email or "",
            password_hash=hash_password(secrets.token_hex(32)),
            role="user",
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row


def _issue_jwt(user: UserEntity) -> tuple[str, str]:
    repo = RedisSessionRepository()
    at, a_jti, a_ttl = create_access_token(user.username, user.role)
    rt, r_jti, r_ttl = create_refresh_token(user.username, user.role)
    repo.save_access(a_jti, user.username, a_ttl)
    repo.save_refresh(user.username, r_jti, r_ttl)
    return at, rt


async def _get(url: str, headers: dict | None = None) -> dict:
    return await asyncio.to_thread(
        lambda: http.get(url, headers=headers or {}, timeout=10).json()
    )


async def _post_form(url: str, data: dict) -> dict:
    return await asyncio.to_thread(
        lambda: http.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        ).json()
    )


async def _post_json(url: str, data: dict) -> dict:
    return await asyncio.to_thread(lambda: http.post(url, data=data, timeout=10).json())


# ── Naver ────────────────────────────────────────────────────────────────────


@oauth_router.get("/auth/naver")
def naver_login() -> RedirectResponse:
    params = {
        "response_type": "code",
        "client_id": os.getenv("NAVER_CLIENT_ID", ""),
        "redirect_uri": os.getenv("NAVER_REDIRECT_URI", ""),
        "state": secrets.token_urlsafe(16),
    }
    return RedirectResponse(
        f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}", status_code=302
    )


@oauth_router.get("/auth/naver/callback")
async def naver_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return _err_redirect(f"naver_denied:{error or 'no_code'}")
    try:
        token_data = await _post_json(
            "https://nid.naver.com/oauth2.0/token",
            {
                "grant_type": "authorization_code",
                "client_id": os.getenv("NAVER_CLIENT_ID", ""),
                "client_secret": os.getenv("NAVER_CLIENT_SECRET", ""),
                "code": code,
                "state": state or "",
            },
        )
        social_token = token_data.get("access_token")
        if not social_token:
            return _err_redirect("naver_token_failed")

        profile = (
            await _get(
                "https://openapi.naver.com/v1/nid/me",
                {"Authorization": f"Bearer {social_token}"},
            )
        ).get("response", {})
        social_id = str(profile.get("id", ""))
        if not social_id:
            return _err_redirect("naver_profile_failed")

        user = await _find_or_create(
            db,
            username=f"naver_{social_id}",
            nickname=profile.get("nickname")
            or profile.get("name")
            or f"naver_{social_id[:6]}",
            email=profile.get("email") or "",
        )
        at, rt = _issue_jwt(user)
        return _ok_redirect(at, rt)
    except Exception:
        return _err_redirect("naver_error")


# ── Kakao ─────────────────────────────────────────────────────────────────────


@oauth_router.get("/auth/kakao")
def kakao_login() -> RedirectResponse:
    params = {
        "response_type": "code",
        "client_id": os.getenv("KAKAO_CLIENT_ID", ""),
        "redirect_uri": os.getenv("KAKAO_REDIRECT_URI", ""),
    }
    return RedirectResponse(
        f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}", status_code=302
    )


@oauth_router.get("/auth/kakao/callback")
async def kakao_callback(
    code: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return _err_redirect(f"kakao_denied:{error or 'no_code'}")
    try:
        token_data = await _post_form(
            "https://kauth.kakao.com/oauth/token",
            {
                "grant_type": "authorization_code",
                "client_id": os.getenv("KAKAO_CLIENT_ID", ""),
                "client_secret": os.getenv("KAKAO_CLIENT_SECRET", ""),
                "redirect_uri": os.getenv("KAKAO_REDIRECT_URI", ""),
                "code": code,
            },
        )
        social_token = token_data.get("access_token")
        if not social_token:
            return _err_redirect("kakao_token_failed")

        info = await _get(
            "https://kapi.kakao.com/v2/user/me",
            {"Authorization": f"Bearer {social_token}"},
        )
        kakao_id = str(info.get("id", ""))
        if not kakao_id:
            return _err_redirect("kakao_profile_failed")

        props = info.get("properties", {})
        account = info.get("kakao_account", {})
        user = await _find_or_create(
            db,
            username=f"kakao_{kakao_id}",
            nickname=props.get("nickname") or f"kakao_{kakao_id[:6]}",
            email=account.get("email") or "",
        )
        at, rt = _issue_jwt(user)
        return _ok_redirect(at, rt)
    except Exception:
        return _err_redirect("kakao_error")


# ── Google ────────────────────────────────────────────────────────────────────


@oauth_router.get("/auth/google")
def google_login() -> RedirectResponse:
    params = {
        "response_type": "code",
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", ""),
        "scope": "openid email profile",
        "access_type": "offline",
    }
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}",
        status_code=302,
    )


@oauth_router.get("/auth/google/callback")
async def google_callback(
    code: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return _err_redirect(f"google_denied:{error or 'no_code'}")
    try:
        token_data = await _post_json(
            "https://oauth2.googleapis.com/token",
            {
                "code": code,
                "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", ""),
                "grant_type": "authorization_code",
            },
        )
        social_token = token_data.get("access_token")
        if not social_token:
            return _err_redirect("google_token_failed")

        info = await _get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            {"Authorization": f"Bearer {social_token}"},
        )
        google_sub = str(info.get("sub", ""))
        if not google_sub:
            return _err_redirect("google_profile_failed")

        user = await _find_or_create(
            db,
            username=f"google_{google_sub}",
            nickname=info.get("name") or f"google_{google_sub[:6]}",
            email=info.get("email") or "",
        )
        at, rt = _issue_jwt(user)
        return _ok_redirect(at, rt)
    except Exception:
        return _err_redirect("google_error")
