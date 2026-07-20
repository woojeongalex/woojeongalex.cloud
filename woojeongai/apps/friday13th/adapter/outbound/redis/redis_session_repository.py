from __future__ import annotations

from core.matrix.redis_client import get_redis_client

_ACCESS_PREFIX = "jwt:access:"
_REFRESH_PREFIX = "jwt:refresh:"


class RedisSessionRepository:
    def __init__(self) -> None:
        self._r = get_redis_client()

    def save_access(self, jti: str, username: str, ttl: int) -> None:
        self._r.setex(f"{_ACCESS_PREFIX}{jti}", ttl, username)

    def save_refresh(self, username: str, jti: str, ttl: int) -> None:
        self._r.setex(f"{_REFRESH_PREFIX}{username}", ttl, jti)

    def validate_access(self, jti: str) -> str | None:
        return self._r.get(f"{_ACCESS_PREFIX}{jti}")

    def validate_refresh(self, username: str, jti: str) -> bool:
        stored = self._r.get(f"{_REFRESH_PREFIX}{username}")
        return stored == jti

    def revoke(self, username: str, access_jti: str) -> None:
        self._r.delete(f"{_ACCESS_PREFIX}{access_jti}", f"{_REFRESH_PREFIX}{username}")
