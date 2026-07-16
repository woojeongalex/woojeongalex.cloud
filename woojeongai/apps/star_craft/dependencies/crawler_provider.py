from fastapi import Depends

from core.matrix.redis_client import RedisClient, get_redis_client
from star_craft.adapter.outbound.csv.csv_export_gateway import CsvExportGateway
from star_craft.adapter.outbound.redis.redis_crawl_target_repository import (
    RedisCrawlTargetRepository,
)
from star_craft.adapter.outbound.scraping.bs4_web_crawl_gateway import Bs4WebCrawlGateway
from star_craft.app.ports.input.crawler_use_case import CrawlerUseCase
from star_craft.app.ports.output.crawl_target_port import CrawlTargetPort
from star_craft.app.ports.output.csv_export_port import CsvExportPort
from star_craft.app.ports.output.web_crawl_port import WebCrawlPort
from star_craft.app.use_cases.crawler_interactor import CrawlerInteractor


def get_crawl_target_repository(
    client: RedisClient = Depends(get_redis_client),
) -> CrawlTargetPort:
    return RedisCrawlTargetRepository(client=client)


def get_web_crawl_gateway() -> WebCrawlPort:
    return Bs4WebCrawlGateway()


def get_csv_export_gateway() -> CsvExportPort:
    return CsvExportGateway()


def get_crawler_use_case(
    targets: CrawlTargetPort = Depends(get_crawl_target_repository),
    crawler: WebCrawlPort = Depends(get_web_crawl_gateway),
    csv_export: CsvExportPort = Depends(get_csv_export_gateway),
) -> CrawlerUseCase:
    return CrawlerInteractor(targets=targets, crawler=crawler, csv_export=csv_export)
