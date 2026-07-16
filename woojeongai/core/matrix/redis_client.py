"""Redis 연결을 관리하는 공용 클라이언트.

core/matrix/secret_manager.py(Keymaker), core/matrix/local_llm_client.py와
동일한 프로세스 싱글턴 패턴을 따른다. 비밀번호는 기존 REDIS_PASSWORD를
그대로 재사용하고, 호스트/포트는 docker-compose의 redis 서비스에 맞춘
기본값(redis:6379)을 쓴다.
"""

from __future__ import annotations

import os

import redis


class RedisClient:
    _instance: RedisClient | None = None

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        password: str | None = None,
        db: int | None = None,
    ) -> None:
        self._host = host or os.getenv("REDIS_HOST") or "redis"
        self._port = port or int(os.getenv("REDIS_PORT") or 6379)
        self._password = password if password is not None else os.getenv("REDIS_PASSWORD") or None
        self._db = db if db is not None else int(os.getenv("REDIS_DB") or 0)
        self._client: redis.Redis | None = None

    @classmethod
    def instance(cls) -> RedisClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                password=self._password,
                db=self._db,
                decode_responses=True,
            )
        return self._client

    def lrange(self, key: str, start: int = 0, end: int = -1) -> list[str]:
        return self._get_client().lrange(key, start, end)

    def rpush(self, key: str, *values: str) -> int:
        return self._get_client().rpush(key, *values)


def get_redis_client() -> RedisClient:
    return RedisClient.instance()
