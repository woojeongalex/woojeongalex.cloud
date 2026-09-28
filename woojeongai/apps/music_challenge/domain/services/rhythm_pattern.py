"""곡 분석 결과로 리듬 게임 채보를 만든다.

신호 처리(librosa)는 어댑터가 하고, 여기서는 "어느 순간에 어느 레인에 노트를 둘지"만
결정한다. 난수를 쓰지 않으므로 같은 곡이면 언제 만들어도 같은 채보가 나온다.

1. 박자 격자 — 비트 사이를 쪼갠 격자에 소리 시작 순간을 맞춘다(박에서 어긋난 노트 방지).
2. 마디 — 비트를 넷씩 묶어 마디 첫 박이 어디인지 추정한다(4/4 가정).
3. 고르기 — 세기에 "마디 안 위치" 가중치를 곱한 값이 큰 자리부터 목표 밀도까지 채운다.
   정박이 다 차야 엇박으로 넘어가므로 노트가 곡의 박을 따라간다.
4. 레인 — 음이름을 곡 안의 순위로 바꿔 레인에 대응시킨다. 같은 음은 같은 쪽,
   음이 오르면 오른쪽으로 간다. 같은 레인 연타가 너무 빠르면 옆 레인으로 비킨다.
5. 롱노트 — 같은 음이 길게 이어지는 소리를 누르고 있는 노트로 바꾼다. 누르는 동안
   다른 레인의 노트는 계속 나온다(오투잼 방식). 동시에 누르는 롱노트 수는 제한한다.
6. 동시치기 — 어려움에서만, 마디의 첫 박·셋째 박에서 가장 센 순간을 두 개
   (7키는 세 개까지) 동시에 친다.
"""

from bisect import bisect_left, insort
from dataclasses import dataclass

from music_challenge.domain.value_objects.rhythm_vo import (
    RHYTHM_KEYS,
    Onset,
    RhythmAnalysis,
    RhythmDifficulty,
    RhythmNote,
    RhythmSheet,
)


@dataclass(frozen=True)
class _Profile:
    subdiv: int  # 한 박을 몇 칸으로 쪼갤지
    nps: float  # 초당 목표 노트 시점 수(동시치기의 추가 노트 제외)
    min_gap_beats: float  # 노트 사이 최소 간격(박)
    long_min_beats: float  # 롱노트 최소 길이(박)
    long_max_beats: float  # 롱노트 최대 길이(박)
    long_ratio: float  # 롱노트 최대 비율
    max_hold: (
        int  # 동시에 누르고 있을 수 있는 롱노트 수. 0 이면 누르는 동안 다른 노트 없음
    )
    chord_strength: float  # 이보다 센 정박이면 동시치기 후보. 1 초과면 동시치기 없음
    chord_ratio: float
    metric: "_Metric"  # 박자 위계 — 어느 자리를 먼저 채울지


@dataclass(frozen=True)
class _Metric:
    """마디 안 자리별 가중치(4/4 가정). 세기에 이 값을 곱한 순서로 노트를 채운다.

    값이 가파를수록 마디 첫 박에 몰려 규칙적인 채보가 되고, 완만할수록 곡의 엇박까지
    살아난다. 그래서 쉬움은 가파르게, 보통·어려움은 완만하게 쓴다.
    """

    beats: tuple[float, float, float, float]  # 마디 첫·둘·셋·넷째 박
    offbeat: float  # 8분 엇박
    subbeat: float  # 그보다 잘게 쪼갠 엇박


_BEATS_PER_BAR = 4

# 쉬움 — 박에 딱 붙는 규칙적인 채보. 첫 박·셋째 박이 다 차야 나머지로 넘어간다.
_METRIC_PULSE = _Metric(beats=(1.0, 0.35, 0.62, 0.35), offbeat=0.22, subbeat=0.10)
# 보통·어려움 — 정박을 앞세우되 곡이 실제로 센 엇박이면 살아남는다.
_METRIC_SONG = _Metric(beats=(1.0, 0.78, 0.88, 0.78), offbeat=0.42, subbeat=0.22)


# 2026-09-22 난이도를 낮췄다("너무 어려워"). 쉬움은 정박만, 보통은 8분까지, 어려움만 16분.
# 2026-09-28 한 번 더 낮췄다. 난이도마다 노트 밀도를 약 25% 줄이고, 어려움의 최소 간격을
# 8분(0.5박)으로 넓혀 16분 연타를 없앴다. 동시치기는 어려움에만 남기고 수도 줄였다.
# 2026-09-28 박자 위계(metric)를 넣었다. 세기만 보고 고르면 곡은 정박으로 들리는데
# 노트는 엇박에 깔려 헷갈린다.
_PROFILES: dict[tuple[int, RhythmDifficulty], _Profile] = {
    (4, RhythmDifficulty.EASY): _Profile(
        subdiv=1,
        nps=0.8,
        min_gap_beats=1.0,
        long_min_beats=1,
        long_max_beats=4,
        long_ratio=0.06,
        max_hold=0,
        chord_strength=2.0,
        chord_ratio=0.0,
        metric=_METRIC_PULSE,
    ),
    (4, RhythmDifficulty.NORMAL): _Profile(
        subdiv=2,
        nps=1.5,
        min_gap_beats=0.5,
        long_min_beats=1,
        long_max_beats=4,
        long_ratio=0.10,
        max_hold=1,
        chord_strength=2.0,
        chord_ratio=0.0,
        metric=_METRIC_SONG,
    ),
    (4, RhythmDifficulty.HARD): _Profile(
        subdiv=4,
        nps=2.6,
        min_gap_beats=0.5,
        long_min_beats=1,
        long_max_beats=6,
        long_ratio=0.12,
        max_hold=1,
        chord_strength=0.92,
        chord_ratio=0.02,
        metric=_METRIC_SONG,
    ),
    (7, RhythmDifficulty.EASY): _Profile(
        subdiv=1,
        nps=1.0,
        min_gap_beats=1.0,
        long_min_beats=1,
        long_max_beats=4,
        long_ratio=0.06,
        max_hold=0,
        chord_strength=2.0,
        chord_ratio=0.0,
        metric=_METRIC_PULSE,
    ),
    (7, RhythmDifficulty.NORMAL): _Profile(
        subdiv=2,
        nps=2.0,
        min_gap_beats=0.5,
        long_min_beats=1,
        long_max_beats=4,
        long_ratio=0.10,
        max_hold=1,
        chord_strength=2.0,
        chord_ratio=0.0,
        metric=_METRIC_SONG,
    ),
    (7, RhythmDifficulty.HARD): _Profile(
        subdiv=4,
        nps=3.2,
        min_gap_beats=0.5,
        long_min_beats=1,
        long_max_beats=6,
        long_ratio=0.12,
        max_hold=1,
        chord_strength=0.90,
        chord_ratio=0.03,
        metric=_METRIC_SONG,
    ),
}

# 같은 레인을 이보다 빨리 연달아 치게 되면 옆 레인으로 옮긴다(초).
_MIN_SAME_LANE_GAP = 0.4
# 롱노트가 끝난 뒤 같은 레인에 다음 노트가 오기까지 비워 둘 시간(초).
_LANE_RELEASE_GAP = 0.12
# 곡 시작 직후는 준비 시간이라 노트를 두지 않는다(초).
_LEAD_IN = 1.0


def _beat_grid(
    analysis: RhythmAnalysis, subdiv: int
) -> tuple[list[float], float, list[float]]:
    """비트 사이를 subdiv 칸으로 나눈 시각들과 한 박 길이(초), 그리고 쓰인 비트 목록.

    첫 비트 앞과 마지막 비트 뒤도 같은 간격으로 이어 붙인다. 격자 칸 j 는 비트 j // subdiv
    에 속하므로, 마디를 셀 때도 이 비트 목록을 그대로 쓴다.
    """
    beats = list(analysis.beats)
    if len(beats) < 2:
        step = 60.0 / analysis.bpm if analysis.bpm > 0 else 0.5
        beats = [i * step for i in range(int(analysis.duration / step) + 1)]
    intervals = sorted(b - a for a, b in zip(beats, beats[1:]))
    period = intervals[len(intervals) // 2]

    while beats[0] - period > 0:
        beats.insert(0, beats[0] - period)
    while beats[-1] + period < analysis.duration:
        beats.append(beats[-1] + period)

    grid: list[float] = []
    for a, b in zip(beats, beats[1:]):
        grid.extend(a + (b - a) * k / subdiv for k in range(subdiv))
    grid.append(beats[-1])
    return grid, period, beats


def _snap(onsets: list[Onset], grid: list[float]) -> list[tuple[int, Onset]]:
    """소리 시작 순간을 가장 가까운 격자 칸에 붙인다. 같은 칸이면 센 쪽만 남긴다."""
    best: dict[int, Onset] = {}
    for onset in onsets:
        i = bisect_left(grid, onset.time)
        cands = [j for j in (i - 1, i) if 0 <= j < len(grid)]
        j = min(cands, key=lambda k: abs(grid[k] - onset.time))
        if j not in best or onset.strength > best[j].strength:
            best[j] = onset
    return sorted(best.items())


def _downbeat_phase(beats: list[float], onsets: list[Onset], period: float) -> int:
    """마디의 첫 박이 몇 번째 비트인지 추정한다(4/4 가정).

    비트마다 그 비트에 붙은 소리 중 가장 센 것을 모아 넷씩 묶고, 합이 가장 큰 자리를
    첫 박으로 본다. 격자를 얼마나 잘게 쪼갰는지와 상관없이 비트에서 바로 세므로
    같은 곡이면 난이도가 달라도 마디가 어긋나지 않는다.

    곡 전체에서 한 번만 정한다. 중간에 박자가 바뀌는 곡은 맞지 않을 수 있다.
    """
    tol = period * 0.12
    ordered = sorted(onsets, key=lambda o: o.time)
    times = [o.time for o in ordered]
    sums = [0.0] * _BEATS_PER_BAR
    for i, beat in enumerate(beats):
        lo = bisect_left(times, beat - tol)
        hi = bisect_left(times, beat + tol)
        if hi > lo:
            sums[i % _BEATS_PER_BAR] += max(o.strength for o in ordered[lo:hi])
    return max(range(_BEATS_PER_BAR), key=lambda p: sums[p])


def _metric_weight(j: int, profile: _Profile, phase: int) -> float:
    """격자 칸이 마디 안에서 얼마나 중요한 자리인지(0~1)."""
    off = j % profile.subdiv
    if off:
        return (
            profile.metric.offbeat
            if off * 2 == profile.subdiv
            else profile.metric.subbeat
        )
    return profile.metric.beats[(j // profile.subdiv - phase) % _BEATS_PER_BAR]


def _on_strong_beat(j: int, subdiv: int, phase: int) -> bool:
    """마디의 첫 박이나 셋째 박인지. 동시치기는 여기에만 둔다."""
    return j % subdiv == 0 and (j // subdiv - phase) % 2 == 0


def _select(
    snapped: list[tuple[int, Onset]],
    grid: list[float],
    duration: float,
    profile: _Profile,
    phase: int,
) -> list[tuple[int, Onset]]:
    """곡의 박에 맞는 자리부터 고르되 최소 간격을 지키며 목표 개수까지 채운다.

    세기만 보면 조금 더 센 엇박이 마디 첫 박을 이겨, 곡은 정박으로 들리는데 노트는
    엇박에 깔린다. 그래서 세기에 마디 안 위치 가중치를 곱한 값으로 고른다.
    정박이 다 차야 엇박으로 넘어가므로 밀도가 낮을수록 더 굵은 박만 남는다.
    """
    min_cells = max(1, round(profile.min_gap_beats * profile.subdiv))
    target = int((duration - _LEAD_IN) * profile.nps)
    chosen: list[int] = []
    picked: list[tuple[int, Onset]] = []
    ranked = sorted(
        snapped,
        key=lambda p: (-p[1].strength * _metric_weight(p[0], profile, phase), p[0]),
    )
    for j, onset in ranked:
        if len(picked) >= target:
            break
        if grid[j] < _LEAD_IN:
            continue
        k = bisect_left(chosen, j)
        if k > 0 and j - chosen[k - 1] < min_cells:
            continue
        if k < len(chosen) and chosen[k] - j < min_cells:
            continue
        insort(chosen, j)
        picked.append((j, onset))
    return sorted(picked)


def _pitch_ranks(onsets: list[Onset]) -> dict[float, float]:
    """음이름 위치를 이 곡 안에서의 순위(0~1)로 바꾼다.

    곡마다 조(key)가 달라 음이름을 그대로 레인에 대응시키면 몇 레인이 텅 빈다.
    많이 나오는 음이름일수록 넓은 폭을 차지하게 누적 비율의 가운데 값을 쓴다.
    """
    counts: dict[float, int] = {}
    for onset in onsets:
        counts[onset.pitch] = counts.get(onset.pitch, 0) + 1
    total = sum(counts.values()) or 1
    ranks: dict[float, float] = {}
    acc = 0
    for pitch in sorted(counts):
        ranks[pitch] = (acc + counts[pitch] / 2) / total
        acc += counts[pitch]
    return ranks


def _top(items: list[tuple[int, Onset]], key, limit: int) -> set[int]:
    return {j for j, _ in sorted(items, key=key)[:limit]}


class _Lanes:
    """레인마다 언제까지 막혀 있는지(롱노트)와 마지막으로 친 시각."""

    def __init__(self, keys: int) -> None:
        self.keys = keys
        self.busy_until = [0.0] * keys
        self.last_hit = [-10.0] * keys

    def holding(self, time: float) -> int:
        return sum(1 for b in self.busy_until if b - _LANE_RELEASE_GAP > time)

    def pick(self, want: int, time: float, taken: set[int]) -> int | None:
        """want 에서 가까운 순서로, 롱노트가 잡고 있지 않고 방금 치지도 않은 레인."""
        order = sorted(range(self.keys), key=lambda lane: (abs(lane - want), lane))
        free = [
            lane
            for lane in order
            if lane not in taken and self.busy_until[lane] <= time
        ]
        for lane in free:
            if time - self.last_hit[lane] >= _MIN_SAME_LANE_GAP:
                return lane
        return free[0] if free else None  # 모두 방금 쳤으면 간격 조건만 풀어 준다

    def place(self, lane: int, time: float, end: float | None) -> None:
        release = end if end is not None else time
        self.busy_until[lane] = release + _LANE_RELEASE_GAP
        self.last_hit[lane] = release


def _level(notes: list[RhythmNote], duration: float, keys: int) -> int:
    """1~20 의 난이도 숫자. 곡 전체 밀도와 가장 빽빽한 10초 구간 밀도로 정한다."""
    if not notes or duration <= 0:
        return 1
    times = [n.time for n in notes]
    avg = len(times) / duration
    peak, lo = 0.0, 0
    for hi, t in enumerate(times):
        while t - times[lo] > 10.0:
            lo += 1
        peak = max(peak, (hi - lo + 1) / 10.0)
    longs = sum(1 for n in notes if n.end is not None) / len(notes)
    extra = 1 if keys == 7 else 0
    return max(1, min(20, round(avg * 1.6 + peak * 0.6 + longs * 3 + extra)))


def build_sheet(
    analysis: RhythmAnalysis, keys: int, difficulty: RhythmDifficulty
) -> RhythmSheet:
    profile = _PROFILES[(keys, difficulty)]
    grid, beat, beats = _beat_grid(analysis, profile.subdiv)
    cell = beat / profile.subdiv
    snapped = _snap(analysis.onsets, grid)
    phase = _downbeat_phase(beats, analysis.onsets, beat)
    picked = _select(snapped, grid, analysis.duration, profile, phase)
    ranks = _pitch_ranks([o for _, o in picked])

    # 롱노트·동시치기는 곡 전체 비율 상한 안에서 두드러진 것부터 허락한다.
    long_ok = _top(
        [(j, o) for j, o in picked if o.sustain >= profile.long_min_beats * beat],
        key=lambda p: (-p[1].sustain, p[0]),
        limit=int(len(picked) * profile.long_ratio),
    )
    chord_ok = _top(
        [
            (j, o)
            for j, o in picked
            if _on_strong_beat(j, profile.subdiv, phase)
            and o.strength >= profile.chord_strength
        ],
        key=lambda p: (-p[1].strength, p[0]),
        limit=int(len(picked) * profile.chord_ratio),
    )

    lanes = _Lanes(keys)
    notes: list[RhythmNote] = []
    for n, (j, onset) in enumerate(picked):
        time = round(grid[j], 3)
        want = _lane_for(ranks[onset.pitch], keys)
        size = 1
        if j in chord_ok:
            size = 3 if keys == 7 and onset.strength >= 0.99 else 2

        end: float | None = None
        if (
            size == 1
            and j in long_ok
            and lanes.holding(time) < max(1, profile.max_hold)
        ):
            length = min(onset.sustain, profile.long_max_beats * beat)
            if profile.max_hold == 0:
                # 쉬움은 누르는 동안 다른 노트가 없게 다음 노트 반 박 앞에서 끊는다.
                nxt = (
                    grid[picked[n + 1][0]] if n + 1 < len(picked) else analysis.duration
                )
                length = min(length, nxt - time - beat * 0.5)
            length = int(length / cell + 1e-6) * cell
            if length >= profile.long_min_beats * beat - 1e-6:
                end = round(time + length, 3)

        taken: set[int] = set()
        for c in range(size):
            # 동시치기의 둘째 노트는 반대편 손으로 가게 거울 위치를 먼저 본다.
            target = want if c == 0 else (keys - 1 - want if c == 1 else keys // 2)
            lane = lanes.pick(target, time, taken)
            if lane is None:
                break
            taken.add(lane)
            notes.append(RhythmNote(time=time, lane=lane, end=end if c == 0 else None))
            lanes.place(lane, time, end if c == 0 else None)

    notes.sort(key=lambda x: (x.time, x.lane))
    return RhythmSheet(
        keys=keys,
        difficulty=difficulty,
        level=_level(notes, analysis.duration, keys),
        notes=notes,
    )


def _lane_for(rank: float, keys: int) -> int:
    return min(keys - 1, max(0, int(rank * keys)))


def build_all_sheets(analysis: RhythmAnalysis) -> list[RhythmSheet]:
    return [
        build_sheet(analysis, keys, difficulty)
        for keys in RHYTHM_KEYS
        for difficulty in RhythmDifficulty
    ]
