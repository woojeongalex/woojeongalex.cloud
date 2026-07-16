from __future__ import annotations

from star_craft.app.dtos.scraper_dto import ScrapeResult
from star_craft.app.ports.input.scraper_use_case import ScraperUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.csv_export_port import CsvExportPort
from star_craft.app.ports.output.web_scrape_port import WebScrapePort


class ScraperInteractor(ScraperUseCase):
    def __init__(self, targets: CrawlTargetPort, scraper: WebScrapePort, csv_export: CsvExportPort):
        self.targets = targets
        self.scraper = scraper
        self.csv_export = csv_export

    async def scrape(self) -> list[ScrapeResult]:
        crawl_targets = await self.targets.read_targets()

        results: list[ScrapeResult] = []
        for target in crawl_targets:
            results.extend(await self.scraper.scrape(target))

        self.csv_export.export(
            "scrape_results.csv",
            [
                {"website": r.website, "keyword": r.keyword, "snippet": r.snippet}
                for r in results
            ],
        )
        return results
