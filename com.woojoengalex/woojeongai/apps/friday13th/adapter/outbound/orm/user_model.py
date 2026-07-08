"""`users` 테이블 ORM · bcrypt 유틸."""

from typing import Optional

import bcrypt
from sqlmodel import Field, SQLModel


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))


class UserEntity(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=64, index=True)
    nickname: str = Field(max_length=64, index=True)
    email: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    role: str = Field(max_length=32, default="user")
