"""RS256 JWT 검증 의존성 — 모든 컨테이너 공용.

기존 friday13th.adapter.inbound.api.deps.current_user_deps (HS256) 와
병존하며 충돌하지 않는다. 신규 앱은 이 모듈을 사용한다.
"""

from __future__ import annotations

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException

from apps.auth.rbac import Role
from core.security import verify_token
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)


async def get_current_user(authorization: str | None = Header(None)) -> dict:
    """Bearer 토큰 검증 (RS256). Redis 블랙리스트(jti) 조회 포함."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")
    token = authorization[7:].strip()
    try:
        payload = verify_token(token, aud="woojeongalex-api")
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    jti = payload.get("jti", "")
    if not RedisSessionRepository().validate_access(jti):
        raise HTTPException(status_code=401, detail="만료되거나 로그아웃된 토큰입니다.")
    return payload


class RoleChecker:
    """라우터 dependencies=[Depends(RoleChecker(Role.USER))] 형태로 사용."""

    def __init__(self, *allowed: Role) -> None:
        self._allowed = set(allowed)

    def __call__(self, payload: dict = Depends(get_current_user)) -> dict:
        role = payload.get("role", "")
        try:
            r = Role(role)
        except ValueError:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        if r not in self._allowed:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        return payload
