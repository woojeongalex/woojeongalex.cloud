from __future__ import annotations

import asyncio
import logging

import requests
from bs4 import BeautifulSoup, Tag

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.crawler_dto import CrawlResult
from star_craft.app.ports.output.web_crawl_port import WebCrawlPort

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 10


class Bs4WebCrawlGateway(WebCrawlPort):
    """대상 웹사이트 페이지의 링크 중 키워드(링크 텍스트 또는 href)가
    포함된 것을 찾는다."""

    async def crawl(self, target: CrawlTarget) -> list[CrawlResult]:
        return await asyncio.to_thread(self._crawl_sync, target)

    def _crawl_sync(self, target: CrawlTarget) -> list[CrawlResult]:
        response = requests.get(target.website, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        results: list[CrawlResult] = []
        for link in soup.find_all("a", href=True):
            if not isinstance(link, Tag):
                continue
            link_text = link.get_text(strip=True)
            href = str(link["href"])
            if target.keyword in link_text or target.keyword in href:
                results.append(
                    CrawlResult(
                        website=target.website,
                        keyword=target.keyword,
                        found_url=href,
                        link_text=link_text,
                    )
                )

        logger.info(f"[Bs4WebCrawlGateway] {target.website} 크롤링 완료 | 매칭 {len(results)}건")
        return results
