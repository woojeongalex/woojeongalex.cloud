from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_SECRET = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
_ALGORITHM = "HS256"
_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL_SECONDS", 3600))  # 1시간
_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL_SECONDS", 604800))  # 7일


def _make_token(sub: str, role: str, token_type: str, ttl: int) -> tuple[str, str]:
    """(token_str, jti) 반환"""
    jti = str(uuid.uuid4())
    payload = {
        "sub": sub,
        "role": role,
        "type": token_type,
        "jti": jti,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(seconds=ttl),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM), jti


def create_access_token(username: str, role: str = "user") -> tuple[str, str, int]:
    """(access_token, jti, ttl_seconds)"""
    token, jti = _make_token(username, role, "access", _ACCESS_TTL)
    return token, jti, _ACCESS_TTL


def create_refresh_token(username: str, role: str = "user") -> tuple[str, str, int]:
    """(refresh_token, jti, ttl_seconds)"""
    token, jti = _make_token(username, role, "refresh", _REFRESH_TTL)
    return token, jti, _REFRESH_TTL


def decode_token(token: str) -> dict:
    """서명·만료 검증 후 페이로드 반환. 실패 시 jwt.PyJWTError 발생."""
    return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
