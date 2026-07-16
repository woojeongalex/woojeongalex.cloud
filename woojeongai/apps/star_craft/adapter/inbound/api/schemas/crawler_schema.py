from pydantic import BaseModel, Field


class CrawlResultItem(BaseModel):
    website: str
    keyword: str
    found_url: str
    link_text: str


class CrawlResponse(BaseModel):
    count: int
    results: list[CrawlResultItem]


class SubmitCrawlRequest(BaseModel):
    website: str = Field(..., min_length=1, description="크롤링할 대상 웹사이트 URL")
    keyword: str = Field(..., min_length=1, description="찾을 키워드")
