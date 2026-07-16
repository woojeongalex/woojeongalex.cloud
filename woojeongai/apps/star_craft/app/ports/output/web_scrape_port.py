from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.scraper_dto import ScrapeResult


class WebScrapePort(ABC):
    @abstractmethod
    async def scrape(self, target: CrawlTarget) -> list[ScrapeResult]:
        """대상 웹사이트 본문에서 키워드가 포함된 스니펫을 추출한다."""
        pass
