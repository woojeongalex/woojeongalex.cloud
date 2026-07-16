from fastapi import Depends

from core.matrix.redis_client import RedisClient, get_redis_client
from star_craft.adapter.outbound.csv.csv_export_gateway import CsvExportGateway
from star_craft.adapter.outbound.redis.redis_crawl_target_repository import (
    RedisCrawlTargetRepository,
)
from star_craft.adapter.outbound.scraping.bs4_web_scrape_gateway import Bs4WebScrapeGateway
from star_craft.app.ports.input.scraper_use_case import ScraperUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.csv_export_port import CsvExportPort
from star_craft.app.ports.output.web_scrape_port import WebScrapePort
from star_craft.app.use_cases.scraper_interactor import ScraperInteractor


def get_crawl_target_repository(
    client: RedisClient = Depends(get_redis_client),
) -> CrawlTargetPort:
    return RedisCrawlTargetRepository(client=client)


def get_web_scrape_gateway() -> WebScrapePort:
    return Bs4WebScrapeGateway()


def get_csv_export_gateway() -> CsvExportPort:
    return CsvExportGateway()


def get_scraper_use_case(
    targets: CrawlTargetPort = Depends(get_crawl_target_repository),
    scraper: WebScrapePort = Depends(get_web_scrape_gateway),
    csv_export: CsvExportPort = Depends(get_csv_export_gateway),
) -> ScraperUseCase:
    return ScraperInteractor(targets=targets, scraper=scraper, csv_export=csv_export)
