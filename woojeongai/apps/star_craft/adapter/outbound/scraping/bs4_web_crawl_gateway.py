from __future__ import annotations

import asyncio
import logging
from collections import Counter, defaultdict

import requests
from bs4 import BeautifulSoup, Tag

from star_craft.app.dtos.crawl_target_dto import CrawlTarget
from star_craft.app.dtos.crawler_dto import CrawlResult
from star_craft.app.ports.output.web_crawl_port import WebCrawlPort

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 10
# User-Agent 없이 요청하면 위키피디아 등 다수 사이트가 봇으로 간주해 403을 준다.
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StarCraftCrawler/1.0)"}

# 차트·목록 페이지의 "행"을 찾기 위한 최소 반복 횟수 (nav·footer 등은 이 수치 미만으로 반복된다)
_MIN_ROW_COUNT = 5
# 모든 행에 동일하게 등장하는 텍스트(재생·다운로드 같은 버튼 라벨)는 항목 데이터가 아니라 UI로 간주
_BOILERPLATE_ROW_RATIO = 0.5
_NON_NAVIGABLE_PREFIXES = ("javascript:", "#")

_RowLinks = list[tuple[str, str]]


def _row_signature(tag: Tag) -> tuple[str, tuple[str, ...]]:
    return (tag.name, tuple(sorted(tag.get("class") or [])))


def _find_list_rows(soup: BeautifulSoup) -> list[Tag]:
    """페이지에서 가장 많이, 가장 풍부하게(링크가 많이) 반복되는 태그를
    표·목록의 각 행으로 간주해 찾는다."""
    groups: dict[tuple[str, tuple[str, ...]], list[Tag]] = defaultdict(list)
    for tag in soup.find_all(True):
        if isinstance(tag, Tag) and tag.find("a", href=True):
            groups[_row_signature(tag)].append(tag)

    candidates = [rows for rows in groups.values() if len(rows) >= _MIN_ROW_COUNT]
    if not candidates:
        return []
    return max(
        candidates,
        key=lambda rows: len(rows) * len(rows[0].find_all("a", href=True)),
    )


def _extract_row_links(row: Tag) -> _RowLinks:
    pairs: _RowLinks = []
    for link in row.find_all("a", href=True):
        if not isinstance(link, Tag):
            continue
        text = link.get_text(strip=True)
        if text:
            pairs.append((str(link["href"]), text))
    return pairs


def _find_boilerplate_texts(rows_links: list[_RowLinks]) -> set[str]:
    row_count: Counter[str] = Counter()
    for pairs in rows_links:
        row_count.update({text for _, text in pairs})
    threshold = max(1, int(len(rows_links) * _BOILERPLATE_ROW_RATIO))
    return {text for text, count in row_count.items() if count >= threshold}


class Bs4WebCrawlGateway(WebCrawlPort):
    """대상 웹사이트에서 반복되는 표·목록의 각 행을 찾아, 행마다 달라지는
    (=UI 버튼이 아닌) 링크만 키워드 기준으로 추출한다. 반복 구조가 없는
    일반 페이지는 전체 링크에서 키워드로 찾는다."""

    async def crawl(self, target: CrawlTarget) -> list[CrawlResult]:
        return await asyncio.to_thread(self._crawl_sync, target)

    def _crawl_sync(self, target: CrawlTarget) -> list[CrawlResult]:
        response = requests.get(
            target.website, headers=_HEADERS, timeout=_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        rows = _find_list_rows(soup)
        results = (
            self._crawl_rows(rows, target)
            if rows
            else self._crawl_all_links(soup, target)
        )

        logger.info(
            f"[Bs4WebCrawlGateway] {target.website} 크롤링 완료 | 매칭 {len(results)}건"
        )
        return results

    def _crawl_rows(self, rows: list[Tag], target: CrawlTarget) -> list[CrawlResult]:
        rows_links = [_extract_row_links(row) for row in rows]
        boilerplate = _find_boilerplate_texts(rows_links)
        keyword_lower = target.keyword.strip().lower()

        results: list[CrawlResult] = []
        for pairs in rows_links:
            real_url = next(
                (h for h, _ in pairs if not h.startswith(_NON_NAVIGABLE_PREFIXES)),
                None,
            )
            for href, text in pairs:
                if text in boilerplate:
                    continue
                if (
                    keyword_lower
                    and keyword_lower not in text.lower()
                    and keyword_lower not in href.lower()
                ):
                    continue
                found_url = (
                    href
                    if not href.startswith(_NON_NAVIGABLE_PREFIXES)
                    else (real_url or href)
                )
                results.append(
                    CrawlResult(
                        website=target.website,
                        keyword=target.keyword,
                        found_url=found_url,
                        link_text=text,
                    )
                )
        return results

    def _crawl_all_links(
        self, soup: BeautifulSoup, target: CrawlTarget
    ) -> list[CrawlResult]:
        keyword_lower = target.keyword.strip().lower()
        results: list[CrawlResult] = []
        for link in soup.find_all("a", href=True):
            if not isinstance(link, Tag):
                continue
            link_text = link.get_text(strip=True)
            href = str(link["href"])
            if (
                not keyword_lower
                or keyword_lower in link_text.lower()
                or keyword_lower in href.lower()
            ):
                results.append(
                    CrawlResult(
                        website=target.website,
                        keyword=target.keyword,
                        found_url=href,
                        link_text=link_text,
                    )
                )
        return results
