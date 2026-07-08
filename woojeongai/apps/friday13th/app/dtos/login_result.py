from dataclasses import dataclass


@dataclass
class LoginResultDto:
    ok: bool
    message: str
    username: str | None = None
    nickname: str | None = None
    role: str | None = None
