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


async def get_optional_user(authorization: str | None = Header(None)) -> dict | None:
    """로그인했으면 토큰 페이로드, 아니면 None.

    비로그인 참여를 허용하면서도 로그인한 사용자는 기록에 남겨야 하는
    엔드포인트용. 토큰이 없거나 유효하지 않아도 401 을 내지 않는다.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
