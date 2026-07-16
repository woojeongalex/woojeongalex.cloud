import os

from fastapi import Depends

from core.matrix.redis_client import RedisClient, get_redis_client
from star_craft.adapter.outbound.jsonl.jsonl_export_gateway import JsonlExportGateway
from star_craft.adapter.outbound.redis.redis_crawl_target_repository import (
    RedisCrawlTargetRepository,
)
from star_craft.adapter.outbound.scraping.bs4_web_crawl_gateway import Bs4WebCrawlGateway
from star_craft.app.ports.input.crawler_use_case import CrawlerUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.jsonl_export_port import JsonlExportPort
from star_craft.app.ports.output.web_crawl_port import WebCrawlPort
from star_craft.app.use_cases.crawler_interactor import CrawlerInteractor

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
_CRAWLED_DIR = os.getenv("STAR_CRAFT_CRAWLED_DIR") or os.path.join(
    _BACKEND_DIR, "resources", "crawled"
)


def get_crawl_target_repository(
    client: RedisClient = Depends(get_redis_client),
) -> CrawlTargetPort:
    return RedisCrawlTargetRepository(client=client)


def get_web_crawl_gateway() -> WebCrawlPort:
    return Bs4WebCrawlGateway()


def get_crawl_export_gateway() -> JsonlExportPort:
    return JsonlExportGateway(output_dir=_CRAWLED_DIR)


def get_crawler_use_case(
    targets: CrawlTargetPort = Depends(get_crawl_target_repository),
    crawler: WebCrawlPort = Depends(get_web_crawl_gateway),
    jsonl_export: JsonlExportPort = Depends(get_crawl_export_gateway),
) -> CrawlerUseCase:
    return CrawlerInteractor(targets=targets, crawler=crawler, jsonl_export=jsonl_export)
