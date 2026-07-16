from dataclasses import dataclass


@dataclass(frozen=True)
class ScrapeResult:
    website: str
    keyword: str
    snippet: str
