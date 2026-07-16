from fastapi import APIRouter, Depends

from star_craft.adapter.inbound.api.schemas.crawler_schema import (
    CrawlResponse,
    CrawlResultItem,
)
from star_craft.app.ports.input.crawler_use_case import CrawlerUseCase
from star_craft.dependencies.crawler_provider import get_crawler_use_case

crawler_router = APIRouter(prefix="/crawler", tags=["crawler"])


@crawler_router.post("/run", summary="Redis에 등록된 대상 크롤링 후 CSV 저장")
async def run_crawler(
    crawler: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlResponse:
    results = await crawler.crawl()
    return CrawlResponse(
        count=len(results),
        results=[
            CrawlResultItem(
                website=r.website,
                keyword=r.keyword,
                found_url=r.found_url,
                link_text=r.link_text,
            )
            for r in results
        ],
    )
