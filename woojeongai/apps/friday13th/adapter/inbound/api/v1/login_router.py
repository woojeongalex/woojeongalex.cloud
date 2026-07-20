from fastapi import APIRouter, Depends, HTTPException
from friday13th.adapter.inbound.api.deps.auth_deps import get_login_use_case
from friday13th.adapter.inbound.api.handlers.auth_inbound_handlers import (
    run_with_db_guard,
)
from friday13th.adapter.inbound.api.schemas.friday13th_request import LoginRequest
from friday13th.adapter.inbound.api.schemas.friday13th_response import LoginResponse
from friday13th.app.ports.input.login_use_case import LoginUseCase
from core.jwt.jwt_util import create_access_token, create_refresh_token
from core.matrix.redis_client import get_redis_client
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)

login_router = APIRouter(prefix="/api/auth", tags=["friday13th-login"])


@login_router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> LoginResponse:
    try:
        out = await run_with_db_guard(
            lambda: use_case.login(request.username, request.password),
            "[login]",
        )
    except ValueError as exc:
        status = 401 if "아이디 또는 비밀번호" in str(exc) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc

    username = out.username or request.username
    role = out.role or "user"

    access_token, access_jti, access_ttl = create_access_token(username, role)
    refresh_token, refresh_jti, refresh_ttl = create_refresh_token(username, role)

    repo = RedisSessionRepository(get_redis_client())
    repo.save_access(access_jti, username, access_ttl)
    repo.save_refresh(username, refresh_jti, refresh_ttl)

    return LoginResponse(
        ok=out.ok,
        message=out.message,
        username=username,
        nickname=out.nickname,
        role=role,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
