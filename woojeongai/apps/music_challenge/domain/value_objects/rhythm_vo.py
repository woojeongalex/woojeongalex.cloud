"""리듬 게임(오투잼식 떨어지는 노트) 값 객체."""

from dataclasses import dataclass
from enum import Enum


class RhythmDifficulty(str, Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


# 지원하는 키 수. 4키는 D F J K, 7키는 오투잼 배치인 S D F Space J K L.
RHYTHM_KEYS: tuple[int, ...] = (4, 7)


@dataclass(frozen=True)
class RhythmNote:
    """노트 하나. 시간은 곡 시작 기준 초. end 가 있으면 누르고 있어야 하는 롱노트다."""

    time: float
    lane: int
    end: float | None = None


@dataclass(frozen=True)
class Onset:
    """곡에서 소리가 새로 시작되는 순간 하나 — 노트 후보.

    time 은 소리가 시작되는 시각(봉우리가 아니라 시작점),
    strength 는 주변 몇 초 안에서 얼마나 두드러지는지(0~1),
    pitch 는 그 순간 가장 강한 음의 음이름 위치(0~1, C=0),
    sustain 은 그 소리가 이어지는 길이(초)다.

    2026-09-28 타악기 여부(percussive)를 뺐다. 저장만 하고 어디서도 쓰지 않던 값인데,
    노트 고르기에 가중치로 넣어 봤더니 드럼 일치율은 그대로면서 정박·규칙성만
    떨어졌다. 드럼은 비트 격자를 맞추는 데 쓰고(어댑터), 채보가 그 격자를 따르면
    자연히 드럼에 얹힌다.
    """

    time: float
    strength: float
    pitch: float
    sustain: float


@dataclass(frozen=True)
class RhythmAnalysis:
    """곡 하나를 분석한 결과. 채보(노트 배치)는 이것만으로 결정된다."""

    duration: float
    bpm: float
    beats: list[float]
    onsets: list[Onset]


@dataclass(frozen=True)
class RhythmSheet:
    """키 수·난이도 하나의 채보."""

    keys: int
    difficulty: RhythmDifficulty
    level: int
    notes: list[RhythmNote]
