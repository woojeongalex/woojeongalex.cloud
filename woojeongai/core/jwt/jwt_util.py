from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

_SECRET = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
_ALGORITHM = "HS256"
_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "3600"))
_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "604800"))


def create_access_token(username: str, role: str = "user") -> tuple[str, str, int]:
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(seconds=_ACCESS_TTL),
        "type": "access",
    }
    token = jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)
    return token, jti, _ACCESS_TTL


def create_refresh_token(username: str, role: str = "user") -> tuple[str, str, int]:
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(seconds=_REFRESH_TTL),
        "type": "refresh",
    }
    token = jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)
    return token, jti, _REFRESH_TTL


def decode_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
