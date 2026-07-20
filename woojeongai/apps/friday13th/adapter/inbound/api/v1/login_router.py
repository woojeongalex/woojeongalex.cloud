from fastapi import APIRouter, Depends, HTTPException
from friday13th.adapter.inbound.api.deps.auth_deps import get_login_use_case
from friday13th.adapter.inbound.api.handlers.auth_inbound_handlers import (
    run_with_db_guard,
)
from friday13th.adapter.inbound.api.schemas.friday13th_request import LoginRequest
from friday13th.adapter.inbound.api.schemas.friday13th_response import LoginResponse
from friday13th.adapter.outbound.redis.redis_session_repository import (
    RedisSessionRepository,
)
from friday13th.app.ports.input.login_use_case import LoginUseCase
from core.jwt.jwt_util import create_access_token, create_refresh_token

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
        repo = RedisSessionRepository()
        at, a_jti, a_ttl = create_access_token(out.username, out.role or "user")
        rt, r_jti, r_ttl = create_refresh_token(out.username, out.role or "user")
        repo.save_access(a_jti, out.username, a_ttl)
        repo.save_refresh(out.username, r_jti, r_ttl)
        return LoginResponse(
            ok=out.ok,
            message=out.message,
            username=out.username,
            nickname=out.nickname,
            role=out.role,
            access_token=at,
            refresh_token=rt,
            token_type="bearer",
        )
    except ValueError as exc:
        status = 401 if "아이디 또는 비밀번호" in str(exc) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc
