from dataclasses import dataclass

from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.value_objects.chart_vo import LyricLine, Note


@dataclass(frozen=True)
class StemFile:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class UploadStemsCommand:
    challenge_id: int
    vocal: StemFile
    instrumental: StemFile | None


@dataclass(frozen=True)
class ChartResult:
    challenge_id: int
    status: ChartStatus
    notes: list[Note]
    duration: float | None
    lyric_lines: list[LyricLine]
    # 도전 화면에서 재생할 반주. 없으면 원곡을 대신 틀어야 한다.
    instrumental_url: str | None
    has_vocal: bool
    error: str | None


@dataclass(frozen=True)
class UploadStemsResult:
    chart: ChartResult
    # 백그라운드 추출에 넘겨, 그 사이 새 업로드가 있었는지 가릴 때 쓴다.
    vocal_key: str
