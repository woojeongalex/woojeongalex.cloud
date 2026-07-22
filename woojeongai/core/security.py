"""RS256 비대칭 JWT 유틸 — auth 게이트웨이 전용.

발급 함수(create_*): JWT_PRIVATE_KEY 필요 → auth 컨테이너에서만 호출.
검증 함수(verify_token): JWT_PUBLIC_KEY만 필요 → 모든 컨테이너 공용.

키는 base64 인코딩된 PEM 또는 PEM 원문을 환경변수로 주입한다.
"""

from __future__ import annotations

import base64
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

_ALGORITHM = "RS256"
_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "600"))  # 10분
_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "604800"))  # 7일
_KID = "woojeongalex-key-1"


def _load_private_key() -> str:
    """호출 시점에 개인키 로드 — import 시점 에러 방지."""
    raw = os.getenv("JWT_PRIVATE_KEY", "")
    if not raw:
        raise RuntimeError("JWT_PRIVATE_KEY 환경변수가 설정되지 않았습니다.")
    if raw.startswith("-----"):
        return raw
    return base64.b64decode(raw).decode()


def _load_public_key() -> str:
    """호출 시점에 공개키 로드."""
    raw = os.getenv("JWT_PUBLIC_KEY", "")
    if not raw:
        raise RuntimeError("JWT_PUBLIC_KEY 환경변수가 설정되지 않았습니다.")
    if raw.startswith("-----"):
        return raw
    return base64.b64decode(raw).decode()


# ── 발급 (auth 컨테이너 전용) ─────────────────────────────────────────────────


def create_access_token(
    username: str,
    role: str = "user",
    expires_min: int | None = None,
) -> tuple[str, str, int]:
    """RS256 액세스 토큰 발급. (token, jti, ttl_seconds) 반환."""
    ttl = (expires_min * 60) if expires_min else _ACCESS_TTL
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(seconds=ttl),
        "aud": "woojeongalex-api",
        "type": "access",
    }
    token = jwt.encode(
        payload,
        _load_private_key(),
        algorithm=_ALGORITHM,
        headers={"kid": _KID},
    )
    return token, jti, ttl


def create_refresh_token(username: str) -> tuple[str, str, int]:
    """RS256 리프레시 토큰 발급. (token, jti, ttl_seconds) 반환."""
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(seconds=_REFRESH_TTL),
        "aud": "woojeongalex-refresh",
        "type": "refresh",
    }
    token = jwt.encode(
        payload,
        _load_private_key(),
        algorithm=_ALGORITHM,
        headers={"kid": _KID},
    )
    return token, jti, _REFRESH_TTL


# ── 검증 (모든 컨테이너 공용) ─────────────────────────────────────────────────


def verify_token(token: str, aud: str) -> dict:
    """RS256 토큰 검증. 실패 시 jwt.PyJWTError 계열 예외 발생."""
    return jwt.decode(
        token,
        _load_public_key(),
        algorithms=["RS256"],
        audience=aud,
    )


# ── 쿠키 설정 ─────────────────────────────────────────────────────────────────

COOKIE_KWARGS: dict = dict(
    domain=".woojeongalex.cloud",
    secure=True,
    httponly=True,
    samesite="lax",
)
