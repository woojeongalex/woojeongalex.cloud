from pydantic import BaseModel


class CrawlResultItem(BaseModel):
    website: str
    keyword: str
    found_url: str
    link_text: str


class CrawlResponse(BaseModel):
    count: int
    results: list[CrawlResultItem]
