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
    """토큰을 아예 안 보냈으면 None(비로그인 참여), 보냈는데 유효하지 않으면 401.

    비로그인 참여를 허용하면서도 로그인한 사용자는 기록에 남겨야 하는 엔드포인트용.

    예전에는 유효하지 않은 토큰도 None 으로 넘겼다. 그러면 세션이 끊긴 사용자의
    제출이 조용히 익명으로 저장돼 랭킹에서 사라진다 — 화면은 로그인 상태로 보이고
    점수도 나오는데 기록에만 안 남으니 알아챌 방법이 없다. 서버를 재시작해 Redis
    세션이 비워지면 로그인한 모든 사용자에게 한꺼번에 일어난다.

    401 을 내면 클라이언트(authFetch)가 토큰을 갱신해 다시 보낸다. 갱신까지
    실패하면 그때는 화면에 오류가 보이므로 사용자가 다시 로그인하고 제출할 수 있다.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return await get_current_user(authorization)
