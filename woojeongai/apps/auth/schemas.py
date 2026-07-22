from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class JwksKey(BaseModel):
    kty: str
    use: str
    alg: str
    kid: str
    n: str
    e: str


class JwksResponse(BaseModel):
    keys: list[JwksKey]
