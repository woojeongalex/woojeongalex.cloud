from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import jwt as pyjwt
from core.jwt.jwt_util import create_access_token, decode_token
from core.matrix.redis_client import get_redis_client
from friday13th.adapter.inbound.api.schemas.friday13th_response import (
    TokenRefreshResponse,
)
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)
from pydantic import BaseModel

token_router = APIRouter(prefix="/api/auth", tags=["friday13th-token"])
_bearer = HTTPBearer(auto_error=False)


class RefreshRequest(BaseModel):
    refresh_token: str


def _get_repo() -> RedisSessionRepository:
    return RedisSessionRepository(get_redis_client())


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Security(_bearer),
    repo: RedisSessionRepository = Depends(_get_repo),
) -> dict:
    """Authorization: Bearer <access_token> 검증 → payload 반환."""
    if not creds:
        raise HTTPException(status_code=401, detail="인증 토큰이 없습니다.")
    try:
        payload = decode_token(creds.credentials)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="액세스 토큰이 아닙니다.")

    jti = payload.get("jti", "")
    if not repo.validate_access(jti):
        raise HTTPException(
            status_code=401, detail="만료되었거나 로그아웃된 세션입니다."
        )

    return payload


@token_router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(body: RefreshRequest) -> TokenRefreshResponse:
    """Refresh token으로 새 Access token 발급."""
    try:
        payload = decode_token(body.refresh_token)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token이 만료되었습니다.")
    except pyjwt.PyJWTError:
        raise HTTPException(
            status_code=401, detail="유효하지 않은 refresh token입니다."
        )

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token이 아닙니다.")

    username = payload.get("sub", "")
    jti = payload.get("jti", "")
    role = payload.get("role", "user")

    repo = _get_repo()
    if not repo.validate_refresh(username, jti):
        raise HTTPException(
            status_code=401, detail="만료되었거나 폐기된 refresh token입니다."
        )

    new_token, new_jti, new_ttl = create_access_token(username, role)
    repo.save_access(new_jti, username, new_ttl)

    return TokenRefreshResponse(access_token=new_token)


@token_router.post("/logout", status_code=204)
def logout(
    payload: dict = Depends(get_current_user),
    repo: RedisSessionRepository = Depends(_get_repo),
) -> None:
    """현재 세션 토큰 폐기 (Redis에서 삭제)."""
    repo.revoke(payload["sub"], payload["jti"])


@token_router.get("/me")
def me(payload: dict = Depends(get_current_user)) -> dict:
    """현재 로그인 사용자 정보 반환."""
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
    }
