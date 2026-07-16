import os

from fastapi import Depends

from core.matrix.redis_client import RedisClient, get_redis_client
from star_craft.adapter.outbound.jsonl.jsonl_export_gateway import JsonlExportGateway
from star_craft.adapter.outbound.redis.redis_crawl_target_repository import (
    RedisCrawlTargetRepository,
)
from star_craft.adapter.outbound.scraping.bs4_web_scrape_gateway import Bs4WebScrapeGateway
from star_craft.app.ports.input.scraper_use_case import ScraperUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.jsonl_export_port import JsonlExportPort
from star_craft.app.ports.output.keyword_parser_port import KeywordParserPort
from star_craft.app.ports.output.web_scrape_port import WebScrapePort
from star_craft.app.use_cases.scraper_interactor import ScraperInteractor
from star_craft.dependencies.keyword_parser_provider import get_keyword_parser

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
_SCRAPED_DIR = os.getenv("STAR_CRAFT_SCRAPED_DIR") or os.path.join(
    _BACKEND_DIR, "resources", "scraped"
)


def get_crawl_target_repository(
    client: RedisClient = Depends(get_redis_client),
) -> CrawlTargetPort:
    return RedisCrawlTargetRepository(client=client)


def get_web_scrape_gateway() -> WebScrapePort:
    return Bs4WebScrapeGateway()


def get_scrape_export_gateway() -> JsonlExportPort:
    return JsonlExportGateway(output_dir=_SCRAPED_DIR)


def get_scraper_use_case(
    targets: CrawlTargetPort = Depends(get_crawl_target_repository),
    scraper: WebScrapePort = Depends(get_web_scrape_gateway),
    jsonl_export: JsonlExportPort = Depends(get_scrape_export_gateway),
    keyword_parser: KeywordParserPort = Depends(get_keyword_parser),
) -> ScraperUseCase:
    return ScraperInteractor(
        targets=targets, scraper=scraper, jsonl_export=jsonl_export, keyword_parser=keyword_parser
    )
