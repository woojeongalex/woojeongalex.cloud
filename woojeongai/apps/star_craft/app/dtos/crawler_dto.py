from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlResult:
    website: str
    keyword: str
    found_url: str
    link_text: str
