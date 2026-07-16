from fastapi import APIRouter, Depends

from star_craft.adapter.inbound.api.schemas.scraper_schema import (
    ScrapeResponse,
    ScrapeResultItem,
    SubmitScrapeRequest,
)
from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.scraper_dto import ScrapeResult
from star_craft.app.ports.input.scraper_use_case import ScraperUseCase
from star_craft.dependencies.scraper_provider import get_scraper_use_case

scraper_router = APIRouter(prefix="/scraper", tags=["scraper"])


def _to_response(results: list[ScrapeResult]) -> ScrapeResponse:
    return ScrapeResponse(
        count=len(results),
        results=[
            ScrapeResultItem(website=r.website, keyword=r.keyword, snippet=r.snippet)
            for r in results
        ],
    )


@scraper_router.post("/run", summary="Redis에 이미 등록된 대상 스크래핑 후 JSONL 누적 저장")
async def run_scraper(
    scraper: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeResponse:
    results = await scraper.scrape()
    return _to_response(results)


@scraper_router.post("/submit", summary="대상 하나를 등록하고 즉시 스크래핑")
async def submit_scraper(
    request: SubmitScrapeRequest,
    scraper: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeResponse:
    results = await scraper.submit(CrawlTarget(website=request.website, keyword=request.keyword))
    return _to_response(results)
