"""[Layer: Domain] Bard 보컬 MR 카탈로그 (인메모리 · DB 미저장)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VocalCatalogItem:
    id: str
    title: str
    artist: str
    bpm: int
    key: str
    range_label: str
    mr_track_name: str
    mr_description: str


VOCAL_CATALOG: tuple[VocalCatalogItem, ...] = (
    VocalCatalogItem(
        id="spring-day",
        title="봄날",
        artist="방탄소년단",
        bpm=108,
        key="Db Major",
        range_label="중음역 · 감성 발라드",
        mr_track_name="봄날 MR (Studio)",
        mr_description="피아노·스트링 중심 MR. 호흡과 감정선 연습용",
    ),
    VocalCatalogItem(
        id="through-the-night",
        title="밤편지",
        artist="아이유",
        bpm=72,
        key="G Major",
        range_label="저중음역 · 어쿠스틱 발라드",
        mr_track_name="밤편지 MR (Acoustic)",
        mr_description="기타·피아노 어쿠스틱 MR. 섬세한 다이내믹 연습",
    ),
    VocalCatalogItem(
        id="defying-gravity",
        title="Defying Gravity",
        artist="Wicked (Musical)",
        bpm=138,
        key="Db Major",
        range_label="고음역 · 뮤지컬 넘버",
        mr_track_name="Defying Gravity MR (Orchestra)",
        mr_description="오케스트라 MR. 고음·벨팅 표현 연습",
    ),
    VocalCatalogItem(
        id="dynamite",
        title="Dynamite",
        artist="방탄소년단",
        bpm=114,
        key="C Major",
        range_label="중고음역 · 팝 댄스",
        mr_track_name="Dynamite MR (Disco Pop)",
        mr_description="디스코 팝 MR. 리듬·박자 정확도 연습",
    ),
)


def find_vocal_catalog_by_query(raw_query: str) -> list[VocalCatalogItem]:
    needle = raw_query.strip().lower()
    if not needle:
        return []
    return [
        item
        for item in VOCAL_CATALOG
        if needle in item.title.lower()
        or needle in item.artist.lower()
        or needle in item.mr_track_name.lower()
        or needle in item.mr_description.lower()
        or needle in item.id.lower()
    ]
