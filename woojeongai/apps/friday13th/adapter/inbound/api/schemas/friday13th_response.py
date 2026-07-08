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


class UsernameCheckResponse(BaseModel):
    available: bool
