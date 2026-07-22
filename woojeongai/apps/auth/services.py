"""OAuth Provider 연동 + RS256 JWT 발급 오케스트레이션."""

from __future__ import annotations

import asyncio
import os
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests as http
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, create_refresh_token
from friday13th.adapter.outbound.orm.user_model import UserEntity, hash_password
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)


# ── HTTP 헬퍼 ─────────────────────────────────────────────────────────────────


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


# ── 로그인 이벤트 기록 ─────────────────────────────────────────────────────────


async def _record_login_event(
    db: AsyncSession,
    user: UserEntity,
    provider: str,
    ip_address: str | None,
) -> None:
    now = datetime.now(timezone.utc)

    # last_login_at 갱신
    await db.execute(
        text("UPDATE users SET last_login_at = :ts WHERE id = :uid"),
        {"ts": now, "uid": user.id},
    )

    # login_events 기록
    await db.execute(
        text(
            "INSERT INTO login_events (user_id, username, nickname, email, provider, ip_address, logged_in_at)"
            " VALUES (:uid, :uname, :nick, :email, :prov, :ip, :ts)"
        ),
        {
            "uid": user.id,
            "uname": user.username,
            "nick": user.nickname,
            "email": user.email or "",
            "prov": provider,
            "ip": ip_address,
            "ts": now,
        },
    )
    await db.commit()

    # 비동기 알림 (실패해도 로그인은 정상 처리)
    try:
        from apps.auth.login_notifier import notify_login
        await notify_login(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email or "",
            provider=provider,
            ip_address=ip_address,
            logged_in_at=now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("[auth][login_event] 알림 실패: %s", e)


# ── 공통 유저 조회/생성 ────────────────────────────────────────────────────────


async def find_or_create_user(
    db: AsyncSession,
    username: str,
    nickname: str,
    email: str,
    provider: str = "unknown",
    ip_address: str | None = None,
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

    await _record_login_event(db, row, provider, ip_address)
    return row


# ── RS256 JWT 발급 ─────────────────────────────────────────────────────────────


def issue_token_pair(user: UserEntity) -> tuple[str, str]:
    """RS256 access/refresh 토큰 발급 후 Redis 저장. (at, rt) 반환."""
    repo = RedisSessionRepository()
    at, a_jti, a_ttl = create_access_token(user.username, user.role)
    rt, r_jti, r_ttl = create_refresh_token(user.username)
    repo.save_access(a_jti, user.username, a_ttl)
    repo.save_refresh(user.username, r_jti, r_ttl)
    return at, rt


# ── Naver OAuth ───────────────────────────────────────────────────────────────


def naver_authorize_url() -> str:
    params = {
        "response_type": "code",
        "client_id": os.getenv("NAVER_CLIENT_ID", ""),
        "redirect_uri": os.getenv("NAVER_REDIRECT_URI", ""),
        "state": secrets.token_urlsafe(16),
    }
    return f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}"


async def naver_fetch_user(code: str, state: str) -> dict | None:
    token_data = await _post_json(
        "https://nid.naver.com/oauth2.0/token",
        {
            "grant_type": "authorization_code",
            "client_id": os.getenv("NAVER_CLIENT_ID", ""),
            "client_secret": os.getenv("NAVER_CLIENT_SECRET", ""),
            "code": code,
            "state": state,
        },
    )
    social_token = token_data.get("access_token")
    if not social_token:
        return None
    profile = (
        await _get(
            "https://openapi.naver.com/v1/nid/me",
            {"Authorization": f"Bearer {social_token}"},
        )
    ).get("response", {})
    social_id = str(profile.get("id", ""))
    if not social_id:
        return None
    return {
        "username": f"naver_{social_id}",
        "nickname": profile.get("nickname") or profile.get("name") or f"naver_{social_id[:6]}",
        "email": profile.get("email") or "",
    }


# ── Kakao OAuth ───────────────────────────────────────────────────────────────


def kakao_authorize_url() -> str:
    params = {
        "response_type": "code",
        "client_id": os.getenv("KAKAO_CLIENT_ID", ""),
        "redirect_uri": os.getenv("KAKAO_REDIRECT_URI", ""),
    }
    return f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"


async def kakao_fetch_user(code: str) -> dict | None:
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
        return None
    info = await _get(
        "https://kapi.kakao.com/v2/user/me",
        {"Authorization": f"Bearer {social_token}"},
    )
    kakao_id = str(info.get("id", ""))
    if not kakao_id:
        return None
    props = info.get("properties", {})
    account = info.get("kakao_account", {})
    return {
        "username": f"kakao_{kakao_id}",
        "nickname": props.get("nickname") or f"kakao_{kakao_id[:6]}",
        "email": account.get("email") or "",
    }


# ── Google OAuth ──────────────────────────────────────────────────────────────


def google_authorize_url() -> str:
    params = {
        "response_type": "code",
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", ""),
        "scope": "openid email profile",
        "access_type": "offline",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def google_fetch_user(code: str) -> dict | None:
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
        return None
    info = await _get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        {"Authorization": f"Bearer {social_token}"},
    )
    google_sub = str(info.get("sub", ""))
    if not google_sub:
        return None
    return {
        "username": f"google_{google_sub}",
        "nickname": info.get("name") or f"google_{google_sub[:6]}",
        "email": info.get("email") or "",
    }
