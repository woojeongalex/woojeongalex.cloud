from datetime import datetime

from pydantic import BaseModel, Field

from music_challenge.domain.value_objects.rhythm_vo import RhythmDifficulty


class RhythmSheetSummaryResponse(BaseModel):
    keys: int
    difficulty: RhythmDifficulty
    level: int
    note_count: int


class RhythmChartResponse(BaseModel):
    challenge_id: int
    # empty | processing | ready | failed
    status: str
    bpm: float | None
    duration: float | None
    audio_url: str | None
    sheets: list[RhythmSheetSummaryResponse]
    error: str | None


class RhythmSheetResponse(BaseModel):
    challenge_id: int
    keys: int
    difficulty: RhythmDifficulty
    level: int
    bpm: float | None
    duration: float | None
    audio_url: str | None
    # [time, lane, end|null] — 노트가 수천 개라 객체 대신 배열로 보낸다.
    notes: list[tuple[float, int, float | None]]


class RhythmPlayRequest(BaseModel):
    # [lane, down, up] — 곡 기준 초(지연 보정 후)
    presses: list[tuple[int, float, float]] = Field(max_length=20000)


class RhythmPlayResponse(BaseModel):
    score: int
    accuracy: float
    max_combo: int
    cool: int
    good: int
    bad: int
    miss: int
    rank: int | None
    best_score: int | None
    is_personal_best: bool


class RhythmRankingEntryResponse(BaseModel):
    rank: int
    nickname: str
    score: int
    accuracy: float
    max_combo: int
    achieved_at: datetime


class RhythmStandingResponse(BaseModel):
    rank: int
    best_score: int


class RhythmRankingResponse(BaseModel):
    items: list[RhythmRankingEntryResponse]
    me: RhythmStandingResponse | None = None
