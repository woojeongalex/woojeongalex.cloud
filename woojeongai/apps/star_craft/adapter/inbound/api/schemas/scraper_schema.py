from pydantic import BaseModel, Field


class ScrapeResultItem(BaseModel):
    website: str
    keyword: str
    snippet: str


class ScrapeResponse(BaseModel):
    count: int
    results: list[ScrapeResultItem]


class SubmitScrapeRequest(BaseModel):
    website: str = Field(..., min_length=1, description="스크래핑할 대상 웹사이트 URL")
    keyword: str = Field(..., min_length=1, description="찾을 키워드")


class CommandScrapeRequest(BaseModel):
    website: str = Field(..., min_length=1, description="스크래핑할 대상 웹사이트 URL")
    command: str = Field(..., min_length=1, description="무엇을 찾을지 자연어로 적은 명령")
