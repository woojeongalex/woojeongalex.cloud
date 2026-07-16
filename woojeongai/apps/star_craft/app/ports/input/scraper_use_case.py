from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.scraper_dto import ScrapeResult


class ScraperUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/scraper_router.py 와 대응."""

    @abstractmethod
    async def scrape(self) -> list[ScrapeResult]:
        """Redis에 등록된 모든 대상을 스크래핑하고 결과를 CSV로 저장한다."""
        pass
