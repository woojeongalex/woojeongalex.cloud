from pydantic import BaseModel, Field


class NoteSchema(BaseModel):
    start: float
    end: float
    midi: int


class LyricLineSchema(BaseModel):
    text: str = Field(max_length=200)
    start: float | None = None


class ChartResponse(BaseModel):
    challenge_id: int
    # empty | processing | ready | failed
    status: str
    # vocal | instrument
    melody_source: str
    # piano | guitar | violin | flute | saxophone | other. 보컬이면 null
    instrument: str | None
    notes: list[NoteSchema]
    duration: float | None
    lyric_lines: list[LyricLineSchema]
    backing_url: str | None
    has_melody: bool
    error: str | None


class UpdateLyricsRequest(BaseModel):
    lines: list[LyricLineSchema] = Field(max_length=300)
