from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.crawler_dto import CrawlResult


class CrawlerUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/crawler_router.py 와 대응."""

    @abstractmethod
    async def crawl(self) -> list[CrawlResult]:
        """Redis에 등록된 모든 대상을 크롤링하고 결과를 CSV로 저장한다."""
        pass
