from fastapi import APIRouter, Depends, HTTPException, Query
from friday13th.adapter.inbound.api.deps.auth_deps import get_signup_use_case
from friday13th.adapter.inbound.api.handlers.auth_inbound_handlers import run_with_db_guard
from friday13th.adapter.inbound.api.schemas.friday13th_request import SignupRequest
from friday13th.adapter.inbound.api.schemas.friday13th_response import (
    SignupResponse,
    UsernameCheckResponse,
)
from friday13th.app.ports.input.signup_use_case import SignupUseCase
from friday13th.domain.entities.friday13th import UserAccount

signup_router = APIRouter(prefix="/api/auth", tags=["friday13th-signup"])


@signup_router.get("/check-id", response_model=UsernameCheckResponse)
async def check_username(
    username: str = Query(..., min_length=1),
    use_case: SignupUseCase = Depends(get_signup_use_case),
) -> UsernameCheckResponse:
    try:
        available = await run_with_db_guard(
            lambda: use_case.is_username_available(username),
            "[check-id]",
        )
        return UsernameCheckResponse(available=available)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@signup_router.get("/check-nickname", response_model=UsernameCheckResponse)
async def check_nickname(
    nickname: str = Query(..., min_length=1),
    use_case: SignupUseCase = Depends(get_signup_use_case),
) -> UsernameCheckResponse:
    try:
        available = await run_with_db_guard(
            lambda: use_case.is_nickname_available(nickname),
            "[check-nickname]",
        )
        return UsernameCheckResponse(available=available)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@signup_router.post("/signup", response_model=SignupResponse)
async def signup(
    request: SignupRequest,
    use_case: SignupUseCase = Depends(get_signup_use_case),
) -> SignupResponse:
    try:
        account = UserAccount(
            username=request.username,
            nickname=request.nickname,
            email=request.email,
            password=request.password,
            role="user",
        )
        await run_with_db_guard(
            lambda: use_case.signup(account, request.password_confirm),
            "[signup]",
        )
        return SignupResponse(ok=True, message="회원가입이 완료되었습니다.")
    except ValueError as exc:
        status = 409 if "이미 사용" in str(exc) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc
