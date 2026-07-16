from pydantic import BaseModel


class ScrapeResultItem(BaseModel):
    website: str
    keyword: str
    snippet: str


class ScrapeResponse(BaseModel):
    count: int
    results: list[ScrapeResultItem]
