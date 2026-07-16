from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.crawler_dto import CrawlResult


class CrawlerUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/crawler_router.py 와 대응."""

    @abstractmethod
    async def crawl(self) -> list[CrawlResult]:
        """Redis에 이미 등록된 모든 대상을 크롤링하고 결과를 JSONL에 누적 저장한다."""
        pass

    @abstractmethod
    async def submit(self, target: CrawlTarget) -> list[CrawlResult]:
        """대상 하나를 Redis에 등록하고 즉시 크롤링해 결과를 반환한다."""
        pass

    @abstractmethod
    async def submit_from_command(self, website: str, command: str) -> list[CrawlResult]:
        """자연어 명령에서 키워드를 이해해 대상을 등록하고 즉시 크롤링한다."""
        pass
