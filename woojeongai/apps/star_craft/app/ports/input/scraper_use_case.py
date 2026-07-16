from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.scraper_dto import ScrapeResult


class ScraperUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/scraper_router.py 와 대응."""

    @abstractmethod
    async def scrape(self) -> list[ScrapeResult]:
        """Redis에 이미 등록된 모든 대상을 스크래핑하고 결과를 JSONL에 누적 저장한다."""
        pass

    @abstractmethod
    async def submit(self, target: CrawlTarget) -> list[ScrapeResult]:
        """대상 하나를 Redis에 등록하고 즉시 스크래핑해 결과를 반환한다."""
        pass
