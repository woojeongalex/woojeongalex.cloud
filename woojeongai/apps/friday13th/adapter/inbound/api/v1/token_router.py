"""JWT 토큰 검증 / 갱신 / 로그아웃."""

from __future__ import annotations

import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel

from core.jwt.jwt_util import create_access_token, decode_token
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)

token_router = APIRouter(prefix="/api/auth", tags=["token"])


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    username: str
    role: str


async def _get_current_user(authorization: str | None = Header(None)) -> dict:
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
    repo = RedisSessionRepository()
    if not repo.validate_access(jti):
        raise HTTPException(status_code=401, detail="만료되거나 로그아웃된 토큰입니다.")
    return payload


@token_router.get("/me", response_model=MeResponse)
async def me(payload: dict = Depends(_get_current_user)) -> MeResponse:
    return MeResponse(username=payload["sub"], role=payload.get("role", "user"))


@token_router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(body: RefreshRequest) -> AccessTokenResponse:
    try:
        payload = decode_token(body.refresh_token)
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
        raise HTTPException(status_code=401, detail="만료되거나 로그아웃된 토큰입니다.")

    new_token, new_jti, ttl = create_access_token(username, role)
    repo.save_access(new_jti, username, ttl)
    return AccessTokenResponse(access_token=new_token)


@token_router.post("/logout")
async def logout(payload: dict = Depends(_get_current_user)) -> dict:
    username = payload["sub"]
    jti = payload.get("jti", "")
    repo = RedisSessionRepository()
    repo.revoke(username, jti)
    return {"ok": True, "message": "로그아웃되었습니다."}
