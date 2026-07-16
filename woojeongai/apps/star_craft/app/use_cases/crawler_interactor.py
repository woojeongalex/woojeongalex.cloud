from __future__ import annotations

from star_craft.app.dtos.crawler_dto import CrawlResult
from star_craft.app.ports.input.crawler_use_case import CrawlerUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.jsonl_export_port import JsonlExportPort
from star_craft.app.ports.output.web_crawl_port import WebCrawlPort


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

        self.jsonl_export.export(
            "crawl_results.jsonl",
            [
                {
                    "website": r.website,
                    "keyword": r.keyword,
                    "found_url": r.found_url,
                    "link_text": r.link_text,
                }
                for r in results
            ],
        )
        return results
