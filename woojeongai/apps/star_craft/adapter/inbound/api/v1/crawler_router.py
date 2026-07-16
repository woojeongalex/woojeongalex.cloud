from fastapi import APIRouter, Depends

from star_craft.adapter.inbound.api.schemas.crawler_schema import (
    CrawlResponse,
    CrawlResultItem,
    SubmitCrawlRequest,
)
from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.crawler_dto import CrawlResult
from star_craft.app.ports.input.crawler_use_case import CrawlerUseCase
from star_craft.dependencies.crawler_provider import get_crawler_use_case

crawler_router = APIRouter(prefix="/crawler", tags=["crawler"])


def _to_response(results: list[CrawlResult]) -> CrawlResponse:
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


@crawler_router.post("/run", summary="Redis에 이미 등록된 대상 크롤링 후 JSONL 누적 저장")
async def run_crawler(
    crawler: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlResponse:
    results = await crawler.crawl()
    return _to_response(results)


@crawler_router.post("/submit", summary="대상 하나를 등록하고 즉시 크롤링")
async def submit_crawler(
    request: SubmitCrawlRequest,
    crawler: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlResponse:
    results = await crawler.submit(CrawlTarget(website=request.website, keyword=request.keyword))
    return _to_response(results)
