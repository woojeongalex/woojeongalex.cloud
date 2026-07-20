from __future__ import annotations

import logging

from core.matrix.redis_client import RedisClient

logger = logging.getLogger(__name__)

_ACCESS_PREFIX = "jwt:access:"  # jwt:access:{jti}  → username
_REFRESH_PREFIX = "jwt:refresh:"  # jwt:refresh:{username} → jti


class RedisSessionRepository:
    """JWT 토큰을 Redis에 저장·검증·폐기한다."""

    def __init__(self, client: RedisClient) -> None:
        self._r = client

    # ── 저장 ──────────────────────────────────────────────────────────────────

    def save_access(self, jti: str, username: str, ttl: int) -> None:
        self._r.setex(f"{_ACCESS_PREFIX}{jti}", ttl, username)
        logger.debug(
            "[Session] access 저장 jti=%s username=%s ttl=%ds", jti, username, ttl
        )

    def save_refresh(self, username: str, jti: str, ttl: int) -> None:
        self._r.setex(f"{_REFRESH_PREFIX}{username}", ttl, jti)
        logger.debug(
            "[Session] refresh 저장 username=%s jti=%s ttl=%ds", username, jti, ttl
        )

    # ── 검증 ──────────────────────────────────────────────────────────────────

    def validate_access(self, jti: str) -> str | None:
        """Redis에 살아있는 jti면 username 반환, 없으면 None."""
        return self._r.get(f"{_ACCESS_PREFIX}{jti}")

    def validate_refresh(self, username: str, jti: str) -> bool:
        """저장된 refresh jti와 일치하면 True."""
        stored = self._r.get(f"{_REFRESH_PREFIX}{username}")
        return stored == jti

    # ── 폐기 (로그아웃) ───────────────────────────────────────────────────────

    def revoke(self, username: str, access_jti: str) -> None:
        self._r.delete(
            f"{_ACCESS_PREFIX}{access_jti}",
            f"{_REFRESH_PREFIX}{username}",
        )
        logger.info("[Session] 토큰 폐기 username=%s", username)

    def revoke_access_only(self, jti: str) -> None:
        self._r.delete(f"{_ACCESS_PREFIX}{jti}")
