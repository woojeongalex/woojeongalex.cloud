"""발성 진단 — 채점과 같은 프레임에서 "어떻게 불렀는지"를 읽어 낸다.

점수(karaoke_scoring)는 얼마나 맞혔는지만 말한다. 그것만으로는 "음정 92%"
같은 말밖에 못 한다. 같은 92% 라도 고음에서만 무너진 사람과 음을 늘 아래로
쳐서 부르는 사람은 연습할 것이 다르다.

녹음을 다시 읽지 않는다. 채점이 쓰는 (시각, MIDI) 프레임을 한 번 더 훑을
뿐이라 비용이 거의 없다. 1GB EC2 에서 제출 하나가 수 분씩 걸리던 전례가
있어 새로 신호 처리를 붙이지 않는 쪽으로 만들었다.

값이 모자라 판단할 수 없으면 그 항목만 None 이다. 억지로 숫자를 만들면
코칭이 근거 없는 말을 한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from music_challenge.domain.services.karaoke_scoring import (
    PERFECT_CENTS,
    folded_semitones,
)
from music_challenge.domain.value_objects.chart_vo import Note

# 프레임이 한참 끊겼을 때 그 공백을 통째로 노래한 시간으로 세지 않도록 자른다.
_MAX_FRAME_SEC = 0.1
# 옥타브를 잘못 잡은 프레임(pyin 이 자주 낸다)까지 평균에 넣으면 편향이 엉킨다.
_BIAS_LIMIT_CENTS = 200.0
# 비브라토를 보려면 음이 이 정도는 이어져야 한다.
_VIBRATO_MIN_SEC = 0.4
_VIBRATO_MIN_FRAMES = 8
# 이 정확도 위의 음표만 "편하게 낸 음"으로 보고 편한 음역을 잡는다.
_COMFORT_MIN_RATIO = 0.8
_WEAK_NOTE_RATIO = 0.5


@dataclass(frozen=True)
class VocalTraits:
    """모두 사람이 읽을 단위. 0~100 은 퍼센트."""

    voiced_ratio: int
    """음표 구간에서 실제로 소리를 낸 비율. 낮으면 숨이 짧거나 가사를 놓쳤다."""

    pitch_bias_cents: int | None
    """음정이 쏠린 방향. 양수면 전반적으로 높게, 음수면 낮게 불렀다."""

    flat_ratio: int | None
    """어긋난 순간 중 아래로 쳐진 비율. 70 이상이면 쳐지는 버릇이다."""

    attack_delay_ms: int | None
    """음을 제 음높이로 잡기까지 걸린 시간의 중앙값."""

    vibrato_extent_cents: int | None
    vibrato_rate_hz: float | None
    """긴 음에서의 흔들림 폭과 속도. 5~7Hz·20~100센트면 비브라토, 그보다 느리고
    넓으면 음정이 불안한 것이다."""

    low_accuracy: int | None
    high_accuracy: int | None
    """곡의 중간 음높이를 기준으로 나눈 아래·위 구간 정확도."""

    comfort_low_midi: float | None
    comfort_high_midi: float | None
    """편하게 낸 음들의 음역. 다음 곡을 고를 때 쓴다."""

    weak_note_count: int
    """정확도 50% 미만인 음표 수."""


@dataclass
class _NoteStat:
    voiced: float = 0.0
    elapsed: float = 0.0
    hit: float = 0.0
    onset_delay: float | None = None
    cents: list[float] | None = None
    times: list[float] | None = None


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _vibrato(stat: _NoteStat) -> tuple[float, float] | None:
    """긴 음 하나의 (흔들림 폭 센트, 속도 Hz). 볼 수 없으면 None."""
    cents, times = stat.cents, stat.times
    if not cents or not times or len(cents) < _VIBRATO_MIN_FRAMES:
        return None
    span = times[-1] - times[0]
    if span <= 0:
        return None
    mean = sum(cents) / len(cents)
    deviations = [c - mean for c in cents]
    extent = sum(abs(d) for d in deviations) / len(deviations)
    # 평균선을 몇 번 가로지르는지로 속도를 본다. 한 주기에 두 번 가로지른다.
    crossings = sum(1 for a, b in zip(deviations, deviations[1:]) if (a < 0) != (b < 0))
    return extent, crossings / (2 * span)


def analyze_vocal_traits(
    notes: list[Note], frames: list[tuple[float, float | None]]
) -> VocalTraits | None:
    """frames 는 채점에 쓴 것과 같은 (곡 기준 초, MIDI 또는 None).

    음표가 없거나 소리를 거의 내지 않았으면 None — 진단할 것이 없다.
    """
    if not notes or not frames:
        return None

    stats = [_NoteStat() for _ in notes]
    cursor = 0
    last_time: float | None = None
    bias_samples: list[float] = []
    off_pitch_flat = off_pitch_total = 0

    for t, midi in frames:
        prev = last_time
        last_time = t
        while cursor < len(notes) and t >= notes[cursor].end:
            cursor += 1
        if cursor >= len(notes):
            break
        note = notes[cursor]
        if t < note.start:
            continue

        # 음표 앞의 쉬는 구간을 첫 프레임에 얹으면 "소리 낸 시간"이 부풀어
        # 한 음도 빼먹지 않은 것처럼 보인다. 음표 안쪽만 센다.
        floor = note.start if prev is None else max(note.start, prev)
        dt = min(_MAX_FRAME_SEC, max(0.0, t - floor))
        if dt == 0:
            continue

        s = stats[cursor]
        s.elapsed += dt
        if midi is None:
            continue
        s.voiced += dt

        signed = folded_semitones(midi, note.midi) * 100
        if abs(signed) <= _BIAS_LIMIT_CENTS:
            bias_samples.append(signed)
        if abs(signed) > PERFECT_CENTS:
            off_pitch_total += 1
            if signed < 0:
                off_pitch_flat += 1
        else:
            s.hit += dt
            if s.onset_delay is None:
                s.onset_delay = t - note.start

        if note.end - note.start >= _VIBRATO_MIN_SEC:
            if s.cents is None or s.times is None:
                s.cents, s.times = [], []
            s.cents.append(signed)
            s.times.append(t)

    # 분모는 "프레임이 있었던 시간"이 아니라 악보가 요구한 전체 시간이다.
    # 아예 안 부른 음표는 프레임이 없어서, 프레임 기준으로 세면 없던 일이 된다.
    total_required = sum(note.end - note.start for note in notes)
    total_voiced = sum(s.voiced for s in stats)
    if total_required <= 0 or total_voiced <= 0:
        return None

    accuracies = [
        (note, s, s.hit / s.elapsed if s.elapsed > 0 else 0.0)
        for note, s in zip(notes, stats)
    ]
    sung = [(note, s, acc) for note, s, acc in accuracies if s.voiced > 0]

    # ── 음역 구간별 정확도 — 곡의 가운데 음을 기준으로 나눈다
    low_accuracy = high_accuracy = None
    if len(sung) >= 4:
        middle = _median([note.midi for note, _, _ in sung])
        lows = [acc for note, _, acc in sung if note.midi <= middle]
        highs = [acc for note, _, acc in sung if note.midi > middle]
        if lows:
            low_accuracy = round(100 * sum(lows) / len(lows))
        if highs:
            high_accuracy = round(100 * sum(highs) / len(highs))

    # ── 편한 음역 — 잘 낸 음들이 어디에 모여 있나
    comfort_low = comfort_high = None
    good = sorted(note.midi for note, _, acc in sung if acc >= _COMFORT_MIN_RATIO)
    if len(good) >= 4:
        lo = max(0, math.floor(len(good) * 0.1) - 1)
        hi = min(len(good) - 1, math.ceil(len(good) * 0.9) - 1)
        comfort_low, comfort_high = good[lo], good[hi]

    # ── 음 잡는 시간
    delays = [s.onset_delay for _, s, _ in sung if s.onset_delay is not None]
    attack_delay_ms = round(_median(delays) * 1000) if delays else None

    # ── 비브라토 — 긴 음들의 중앙값
    measured = [v for _, s, _ in sung if (v := _vibrato(s)) is not None]
    vib_extent = vib_rate = None
    if len(measured) >= 3:
        vib_extent = round(_median([e for e, _ in measured]))
        vib_rate = round(_median([r for _, r in measured]), 1)

    return VocalTraits(
        voiced_ratio=min(100, round(100 * total_voiced / total_required)),
        pitch_bias_cents=(
            round(sum(bias_samples) / len(bias_samples)) if bias_samples else None
        ),
        flat_ratio=(
            round(100 * off_pitch_flat / off_pitch_total) if off_pitch_total else None
        ),
        attack_delay_ms=attack_delay_ms,
        vibrato_extent_cents=vib_extent,
        vibrato_rate_hz=vib_rate,
        low_accuracy=low_accuracy,
        high_accuracy=high_accuracy,
        comfort_low_midi=comfort_low,
        comfort_high_midi=comfort_high,
        # 아예 안 부른 음표가 가장 약한 음표다. sung 이 아니라 전체에서 센다.
        weak_note_count=sum(1 for _, _, acc in accuracies if acc < _WEAK_NOTE_RATIO),
    )
