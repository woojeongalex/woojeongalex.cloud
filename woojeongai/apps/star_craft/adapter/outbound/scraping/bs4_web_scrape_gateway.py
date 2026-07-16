from __future__ import annotations

import asyncio
import logging

import requests
from bs4 import BeautifulSoup

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.scraper_dto import ScrapeResult
from star_craft.app.ports.output.web_scrape_port import WebScrapePort

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 10
_TEXT_TAGS = ("p", "li", "h1", "h2", "h3")


class Bs4WebScrapeGateway(WebScrapePort):
    """대상 웹사이트 본문 텍스트 중 키워드가 포함된 문단·항목을 추출한다."""

    async def scrape(self, target: CrawlTarget) -> list[ScrapeResult]:
        return await asyncio.to_thread(self._scrape_sync, target)

    def _scrape_sync(self, target: CrawlTarget) -> list[ScrapeResult]:
        response = requests.get(target.website, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        results: list[ScrapeResult] = []
        for tag in soup.find_all(_TEXT_TAGS):
            text = tag.get_text(strip=True)
            if target.keyword in text:
                results.append(
                    ScrapeResult(website=target.website, keyword=target.keyword, snippet=text)
                )

        logger.info(f"[Bs4WebScrapeGateway] {target.website} 스크래핑 완료 | 매칭 {len(results)}건")
        return results
