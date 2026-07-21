"""MR 검색 스냅샷 — `song_mr_search_lists`."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, func
from sqlmodel import Field, SQLModel


class SongMrSearchListEntity(SQLModel, table=True):
    __tablename__ = "song_mr_search_lists"

    id: Optional[int] = Field(default=None, primary_key=True)
    search_query: str = Field(max_length=256, index=True)
    catalog_song_id: str = Field(max_length=64, index=True)
    title: str = Field(max_length=256)
    artist: str = Field(max_length=256)
    bpm: int = Field(sa_column=Column(Integer, nullable=False))
    song_key: str = Field(max_length=64)
    range_label: str = Field(max_length=128)
    mr_track_name: str = Field(max_length=256)
    mr_description: str = Field(max_length=512)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
