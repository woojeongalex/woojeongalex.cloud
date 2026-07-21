from __future__ import annotations

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException

from core.jwt.jwt_util import decode_token
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)


async def get_current_user(authorization: str | None = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")
    token = authorization[7:].strip()
    try:
        payload = decode_token(token)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    jti = payload.get("jti", "")
    if not RedisSessionRepository().validate_access(jti):
        raise HTTPException(status_code=401, detail="만료되거나 로그아웃된 토큰입니다.")
    return payload


async def require_admin(payload: dict = Depends(get_current_user)) -> dict:
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return payload
