"""노래방 화면의 "악보" — 정답 멜로디 음표와 가사 줄."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    """정답 멜로디의 음표 하나. 시간은 곡 시작 기준 초, 음높이는 MIDI 번호."""

    start: float
    end: float
    midi: int


@dataclass(frozen=True)
class LyricLine:
    """가사 한 줄. start 가 None 이면 아직 타이밍을 맞추지 않은 줄이다."""

    text: str
    start: float | None
