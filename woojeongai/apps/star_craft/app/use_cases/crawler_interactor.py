from __future__ import annotations

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.crawler_dto import CrawlResult
from star_craft.app.ports.input.crawler_use_case import CrawlerUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.jsonl_export_port import JsonlExportPort
from star_craft.app.ports.output.web_crawl_port import WebCrawlPort

_JSONL_FILENAME = "crawl_results.jsonl"


def _to_row(result: CrawlResult) -> dict[str, str]:
    return {
        "website": result.website,
        "keyword": result.keyword,
        "found_url": result.found_url,
        "link_text": result.link_text,
    }


class CrawlerInteractor(CrawlerUseCase):
    def __init__(self, targets: CrawlTargetPort, crawler: WebCrawlPort, jsonl_export: JsonlExportPort):
        self.targets = targets
        self.crawler = crawler
        self.jsonl_export = jsonl_export

    async def crawl(self) -> list[CrawlResult]:
        crawl_targets = await self.targets.read_targets()

        results: list[CrawlResult] = []
        for target in crawl_targets:
            results.extend(await self.crawler.crawl(target))

        self.jsonl_export.export(_JSONL_FILENAME, [_to_row(r) for r in results])
        return results

    async def submit(self, target: CrawlTarget) -> list[CrawlResult]:
        await self.targets.enqueue(target)
        results = await self.crawler.crawl(target)
        self.jsonl_export.export(_JSONL_FILENAME, [_to_row(r) for r in results])
        return results
