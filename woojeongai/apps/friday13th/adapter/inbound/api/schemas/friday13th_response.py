from pydantic import BaseModel


class SignupResponse(BaseModel):
    ok: bool
    message: str


class LoginResponse(BaseModel):
    ok: bool
    message: str
    username: str | None = None
    nickname: str | None = None
    role: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = "bearer"


class UsernameCheckResponse(BaseModel):
    available: bool
