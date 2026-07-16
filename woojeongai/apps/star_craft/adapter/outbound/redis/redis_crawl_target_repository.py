from __future__ import annotations

import asyncio
import json
import logging

from core.matrix.redis_client import RedisClient
from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort

logger = logging.getLogger(__name__)

REDIS_CRAWL_TARGETS_KEY = "star_craft:crawl_targets"


class RedisCrawlTargetRepository(CrawlTargetPort):
    """Redis 리스트(star_craft:crawl_targets)에 JSON으로 등록된
    {"website": "...", "keyword": "..."} 목록을 읽는다."""

    def __init__(self, client: RedisClient):
        self._client = client

    async def read_targets(self) -> list[CrawlTarget]:
        raw_items = await asyncio.to_thread(self._client.lrange, REDIS_CRAWL_TARGETS_KEY)
        logger.info(f"[RedisCrawlTargetRepository] 대상 {len(raw_items)}건 로드")
        return [self._parse(item) for item in raw_items]

    async def enqueue(self, target: CrawlTarget) -> None:
        payload = json.dumps({"website": target.website, "keyword": target.keyword})
        await asyncio.to_thread(self._client.rpush, REDIS_CRAWL_TARGETS_KEY, payload)
        logger.info(f"[RedisCrawlTargetRepository] 대상 등록 | website={target.website} keyword={target.keyword}")

    @staticmethod
    def _parse(raw: str) -> CrawlTarget:
        data = json.loads(raw)
        return CrawlTarget(website=data["website"], keyword=data["keyword"])
