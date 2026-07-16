from fastapi import APIRouter, Depends

from star_craft.adapter.inbound.api.schemas.scraper_schema import (
    ScrapeResponse,
    ScrapeResultItem,
)
from star_craft.app.ports.input.scraper_use_case import ScraperUseCase
from star_craft.dependencies.scraper_provider import get_scraper_use_case

scraper_router = APIRouter(prefix="/scraper", tags=["scraper"])


@scraper_router.post("/run", summary="Redis에 등록된 대상 스크래핑 후 CSV 저장")
async def run_scraper(
    scraper: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeResponse:
    results = await scraper.scrape()
    return ScrapeResponse(
        count=len(results),
        results=[
            ScrapeResultItem(website=r.website, keyword=r.keyword, snippet=r.snippet)
            for r in results
        ],
    )
