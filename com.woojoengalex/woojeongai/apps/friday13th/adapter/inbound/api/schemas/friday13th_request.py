from pydantic import BaseModel


class SignupRequest(BaseModel):
    username: str
    nickname: str
    email: str
    password: str
    password_confirm: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str
