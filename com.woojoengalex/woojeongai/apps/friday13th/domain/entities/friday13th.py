from dataclasses import dataclass


@dataclass
class UserAccount:
    username: str
    nickname: str
    email: str
    password: str
    role: str = "user"
