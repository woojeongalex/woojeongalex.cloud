from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.crawl_target_dto import CrawlTarget


class CrawlTargetPort(ABC):
    @abstractmethod
    async def read_targets(self) -> list[CrawlTarget]:
        """Redis에 등록된 크롤링·스크래핑 대상(웹사이트+키워드) 목록을 읽는다."""
        pass

    @abstractmethod
    async def enqueue(self, target: CrawlTarget) -> None:
        """새 대상(웹사이트+키워드) 하나를 Redis 큐에 등록한다."""
        pass
