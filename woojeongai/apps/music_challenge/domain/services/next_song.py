"""다음 곡 고르기 — 이번에 무엇이 무너졌는지를 보고 고른다.

예전에는 후보 목록의 첫 번째를 집었다. 그 순서가 DB 가 주는 순서라, 7점을
받든 100점을 받든 같은 곡이 나왔다.

지금은 방금 부른 결과에서 읽은 약점에 맞춘다. 규칙은 넷이고, 모두 "다음에
한 곡 더 부르고 싶게" 만드는 쪽이다 — 약점을 정면으로 때리는 곡을 주면
또 무너지고 그만둔다.

- 편한 음역 안에 많이 들어오는 곡을 좋아한다.
- 고음이 무너졌으면 편한 음역 위로 더 올라가는 곡을 싫어한다. 저음도 같다.
- 박자가 흔들렸으면 느린 곡을 좋아한다.

가중치는 음역이 가장 크다. 음이 안 닿으면 나머지는 의미가 없다.
"""

from __future__ import annotations

from dataclasses import dataclass

# 아래·위 구간 정확도가 이만큼 벌어지면 그쪽이 약하다고 본다(퍼센트 포인트).
_RANGE_WEAKNESS_GAP = 15
# 이 아래면 박자가 흔들린 것으로 본다(퍼센트).
_TIMING_WEAK_BELOW = 80
# 이보다 빠른 곡은 박자가 약한 사람에게 부담이다.
_FAST_BPM = 120.0
# 편한 음역을 모를 때 곡의 높낮이를 재는 기준 — 대략 A2~C6.
_VOICE_LOW_MIDI = 45.0
_VOICE_SPAN = 40.0

_W_RANGE = 1.0
_W_OVERSHOOT = 0.6
_W_TEMPO = 0.4


@dataclass(frozen=True)
class SongCandidate:
    challenge_id: int
    same_type: bool
    """방금 부른 곡과 같은 유형인지."""
    low_midi: float
    high_midi: float
    bpm: float | None


@dataclass(frozen=True)
class Weakness:
    """방금 부른 결과에서 읽은 약점. 모르는 항목은 None."""

    comfort_low_midi: float | None
    comfort_high_midi: float | None
    high_is_weak: bool
    low_is_weak: bool
    timing_is_weak: bool

    @property
    def knows_range(self) -> bool:
        return (
            self.comfort_low_midi is not None
            and self.comfort_high_midi is not None
            and self.comfort_high_midi > self.comfort_low_midi
        )


def _range_fit(song: SongCandidate, low: float, high: float) -> float:
    """곡의 음역 중 편한 구간 안에 들어오는 비율. 0~1."""
    span = song.high_midi - song.low_midi
    if span <= 0:
        return 0.0
    shared = min(high, song.high_midi) - max(low, song.low_midi)
    return max(0.0, shared) / span


def _overshoot(
    song: SongCandidate, weakness: Weakness, low: float, high: float
) -> float:
    """약한 쪽으로 편한 음역을 얼마나 벗어나는지. 반음 12개를 1.0 으로 본다."""
    out = 0.0
    if weakness.high_is_weak:
        out += max(0.0, song.high_midi - high) / 12
    if weakness.low_is_weak:
        out += max(0.0, low - song.low_midi) / 12
    return min(1.0, out)


def _reach(midi: float) -> float:
    """사람 목소리 범위(대략 A2~C6)에서 이 음이 얼마나 높은지. 0~1."""
    return max(0.0, min(1.0, (midi - _VOICE_LOW_MIDI) / _VOICE_SPAN))


def _reach_penalty(song: SongCandidate, weakness: Weakness) -> float:
    """편한 음역을 모를 때 쓰는 대체 잣대 — 곡 자체가 얼마나 높은지·낮은지.

    잘 못 부른 사람일수록 편한 음역이 안 잡힌다. 그때 아무 근거도 없다고
    보고 곡 번호 순으로 주면, 정작 도움이 가장 필요한 사람이 가장 엉뚱한
    곡을 받는다. 음역을 몰라도 "고음이 약하다"는 알고 있으니 그것만으로도
    높은 곡을 피할 수 있다.
    """
    out = 0.0
    if weakness.high_is_weak:
        out += _reach(song.high_midi)
    if weakness.low_is_weak:
        out += 1.0 - _reach(song.low_midi)
    return min(1.0, out)


def _tempo_fit(song: SongCandidate) -> float:
    """느릴수록 1 에 가깝다. BPM 을 모르면 중립(0.5)."""
    if song.bpm is None or song.bpm <= 0:
        return 0.5
    return max(0.0, min(1.0, (_FAST_BPM - song.bpm) / 60 + 0.5))


def pick_next_song(candidates: list[SongCandidate], weakness: Weakness) -> int | None:
    """가장 잘 맞는 곡의 challenge_id. 후보가 없으면 None.

    아무 약점도 읽지 못했으면(짧게 불러 잴 것이 없었으면) 곡 번호가 작은 것을
    준다. 호출 측이 이미 해 본 곡을 빼 주므로 매번 같은 곡이 나오지는 않는다.
    """
    if not candidates:
        return None

    low = weakness.comfort_low_midi
    high = weakness.comfort_high_midi
    knows_range = weakness.knows_range
    if not (
        knows_range
        or weakness.high_is_weak
        or weakness.low_is_weak
        or weakness.timing_is_weak
    ):
        return min(candidates, key=lambda c: c.challenge_id).challenge_id

    def fit(song: SongCandidate) -> tuple[float, int]:
        value = 0.0
        if knows_range and low is not None and high is not None:
            value += _W_RANGE * _range_fit(song, low, high)
            value -= _W_OVERSHOOT * _overshoot(song, weakness, low, high)
        else:
            value -= _W_OVERSHOOT * _reach_penalty(song, weakness)
        if weakness.timing_is_weak:
            value += _W_TEMPO * _tempo_fit(song)
        # 동점이면 곡 번호가 작은 쪽 — 매번 같은 순서로 정해져야 설명이 된다.
        return value, -song.challenge_id

    return max(candidates, key=fit).challenge_id


def read_weakness(
    *,
    comfort_low_midi: float | None,
    comfort_high_midi: float | None,
    low_accuracy: int | None,
    high_accuracy: int | None,
    timing_accuracy: int | None,
) -> Weakness:
    """발성 진단과 채점에서 추천이 쓸 것만 추린다."""
    high_weak = low_weak = False
    if low_accuracy is not None and high_accuracy is not None:
        gap = low_accuracy - high_accuracy
        high_weak = gap >= _RANGE_WEAKNESS_GAP
        low_weak = -gap >= _RANGE_WEAKNESS_GAP
    return Weakness(
        comfort_low_midi=comfort_low_midi,
        comfort_high_midi=comfort_high_midi,
        high_is_weak=high_weak,
        low_is_weak=low_weak,
        timing_is_weak=timing_accuracy is not None
        and timing_accuracy < _TIMING_WEAK_BELOW,
    )
