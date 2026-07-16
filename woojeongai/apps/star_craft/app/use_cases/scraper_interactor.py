from __future__ import annotations

import asyncio

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.scraper_dto import ScrapeResult
from star_craft.app.ports.input.scraper_use_case import ScraperUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.jsonl_export_port import JsonlExportPort
from star_craft.app.ports.output.keyword_parser_port import KeywordParserPort
from star_craft.app.ports.output.web_scrape_port import WebScrapePort

_JSONL_FILENAME = "scrape_results.jsonl"


def _to_row(result: ScrapeResult) -> dict[str, str]:
    return {"website": result.website, "keyword": result.keyword, "snippet": result.snippet}


class ScraperInteractor(ScraperUseCase):
    def __init__(
        self,
        targets: CrawlTargetPort,
        scraper: WebScrapePort,
        jsonl_export: JsonlExportPort,
        keyword_parser: KeywordParserPort,
    ):
        self.targets = targets
        self.scraper = scraper
        self.jsonl_export = jsonl_export
        self.keyword_parser = keyword_parser

    async def scrape(self) -> list[ScrapeResult]:
        crawl_targets = await self.targets.read_targets()

        results: list[ScrapeResult] = []
        for target in crawl_targets:
            results.extend(await self.scraper.scrape(target))

        self.jsonl_export.export(_JSONL_FILENAME, [_to_row(r) for r in results])
        return results

    async def submit(self, target: CrawlTarget) -> list[ScrapeResult]:
        await self.targets.enqueue(target)
        results = await self.scraper.scrape(target)
        self.jsonl_export.export(_JSONL_FILENAME, [_to_row(r) for r in results])
        return results

    async def submit_from_command(self, website: str, command: str) -> list[ScrapeResult]:
        keyword = await asyncio.to_thread(self.keyword_parser.extract_keyword, command)
        return await self.submit(CrawlTarget(website=website, keyword=keyword))
