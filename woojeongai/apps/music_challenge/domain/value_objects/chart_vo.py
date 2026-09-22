"""노래방 화면의 "악보" — 정답 멜로디 음표와 가사 줄."""

from dataclasses import dataclass
from enum import Enum


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


class MelodySource(str, Enum):
    """정답 멜로디를 어디서 뽑았는지. 추출 방식과 도전 화면 문구가 달라진다."""

    VOCAL = "vocal"
    INSTRUMENT = "instrument"


class InstrumentKind(str, Enum):
    """연주곡의 멜로디 악기. 화면 표시용이며 추출은 같은 악기 프로필을 쓴다."""

    PIANO = "piano"
    GUITAR = "guitar"
    VIOLIN = "violin"
    FLUTE = "flute"
    SAXOPHONE = "saxophone"
    OTHER = "other"
