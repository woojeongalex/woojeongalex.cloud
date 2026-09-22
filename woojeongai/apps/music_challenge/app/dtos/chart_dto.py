from dataclasses import dataclass

from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.value_objects.chart_vo import (
    InstrumentKind,
    LyricLine,
    MelodySource,
    Note,
)


@dataclass(frozen=True)
class StemFile:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class UploadStemsCommand:
    challenge_id: int
    # 정답을 뽑을 트랙 — 보컬 스템 또는 멜로디 악기 스템
    melody: StemFile
    # 도전할 때 틀어 줄 반주. 없으면 이전에 올린 반주를 유지한다.
    backing: StemFile | None
    melody_source: MelodySource
    instrument: InstrumentKind | None


@dataclass(frozen=True)
class ChartResult:
    challenge_id: int
    status: ChartStatus
    melody_source: MelodySource
    instrument: InstrumentKind | None
    notes: list[Note]
    duration: float | None
    lyric_lines: list[LyricLine]
    # 도전 화면에서 틀 반주. 없으면 원곡을 대신 틀어야 한다.
    backing_url: str | None
    has_melody: bool
    error: str | None


@dataclass(frozen=True)
class UploadStemsResult:
    chart: ChartResult
    # 백그라운드 추출에 넘겨, 그 사이 새 업로드가 있었는지 가릴 때 쓴다.
    melody_key: str
