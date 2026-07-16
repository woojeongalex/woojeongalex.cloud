from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlTarget:
    website: str
    keyword: str
