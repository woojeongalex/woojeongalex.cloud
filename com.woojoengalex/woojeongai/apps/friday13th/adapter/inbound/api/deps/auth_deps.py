"""인증 Use Case 조립 — DB 세션은 여기서만 주입."""

from database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from friday13th.adapter.outbound.pg.login_pg_repository import LoginPgRepository
from friday13th.adapter.outbound.pg.signup_pg_repository import SignupPgRepository
from friday13th.app.ports.input.login_use_case import LoginUseCase
from friday13th.app.ports.input.signup_use_case import SignupUseCase
from friday13th.app.use_cases.login_interactor import LoginInteractor
from friday13th.app.use_cases.signup_interactor import SignupInteractor


def get_signup_use_case(db: AsyncSession = Depends(get_db)) -> SignupUseCase:
    return SignupInteractor(SignupPgRepository(db))


def get_login_use_case(db: AsyncSession = Depends(get_db)) -> LoginUseCase:
    return LoginInteractor(LoginPgRepository(db))
