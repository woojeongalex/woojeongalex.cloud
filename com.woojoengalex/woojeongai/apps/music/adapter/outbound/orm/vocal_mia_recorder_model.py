"""사용자 보컬 입력(마이크·영상·음원) — `user_vocal_recordings`."""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlmodel import Field, SQLModel


class UserVocalRecordingEntity(SQLModel, table=True):
    """performs_vocal의 결과물: 사용자가 제출한 녹음·영상 1건 (평가 세션 1:1)."""

    __tablename__ = "user_vocal_recordings"

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        description="녹음·업로드한 회원. 로그인 연동 시 세션 user_id와 동일해야 함",
    )
    catalog_song_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(64), nullable=True, index=True),
        description="녹음 시점 선택 곡. mr_search_list_id 있으면 MR 행 기준으로 서버 정합",
    )
    mr_search_list_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("song_mr_search_lists.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        description="녹음·분석에 사용한 MR 검색 행 (uses_mr)",
    )
    sing_evaluation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("sing_evaluations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )
    input_source: str = Field(max_length=16, description="mic | video")
    file_name: str = Field(max_length=512, description="원본 파일명 또는 마이크 라벨")
    duration_sec: int = Field(ge=0, default=0)
    content_type: Optional[str] = Field(
        default=None,
        max_length=128,
        description="MIME (예: video/mp4). 미전달 시 null",
    )
    storage_uri: Optional[str] = Field(
        default=None,
        max_length=1024,
        description="서버·오브젝트 스토리지 경로. 업로드 저장 연동 전 null",
    )
    recorded_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
