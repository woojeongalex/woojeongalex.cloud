from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.crawler_dto import CrawlResult


class WebCrawlPort(ABC):
    @abstractmethod
    async def crawl(self, target: CrawlTarget) -> list[CrawlResult]:
        """대상 웹사이트에서 키워드가 포함된 링크를 찾는다."""
        pass
