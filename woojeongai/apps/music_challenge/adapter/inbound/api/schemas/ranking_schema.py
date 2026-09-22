from datetime import datetime

from pydantic import BaseModel


class RankingEntryResponse(BaseModel):
    rank: int
    nickname: str
    score: int
    pitch_accuracy: int | None
    timing_accuracy: int | None
    achieved_at: datetime


class MyStandingResponse(BaseModel):
    rank: int
    best_score: int


class ChallengeRankingResponse(BaseModel):
    items: list[RankingEntryResponse]
    # 로그인했고 이 곡 기록이 있을 때만
    me: MyStandingResponse | None = None


class WeeklyRankingEntryResponse(RankingEntryResponse):
    challenge_id: int
    challenge_title: str


class WeeklyRankingResponse(BaseModel):
    items: list[WeeklyRankingEntryResponse]
