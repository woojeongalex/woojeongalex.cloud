"""[Layer: Use Cases] Bard MR 검색 DTO."""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SongMrHitDto", "SongMrSearchResultDto", "SongMrSearchSaveDto", "BardIntroduceQuery", "BardIntroduceResponse"]


@dataclass(frozen=True)
class SongMrSearchSaveDto:
    search_query: str
    catalog_song_id: str
    title: str
    artist: str
    bpm: int
    song_key: str
    range_label: str
    mr_track_name: str
    mr_description: str


@dataclass(frozen=True)
class SongMrHitDto:
    id: int
    catalog_song_id: str
    title: str
    artist: str
    bpm: int
    song_key: str
    range_label: str
    mr_track_name: str
    mr_description: str


@dataclass(frozen=True)
class BardIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class BardIntroduceResponse:
    id: int
    name: str


@dataclass(frozen=True)
class SongMrSearchResultDto:
    query: str
    hits: list[SongMrHitDto]
    count: int
