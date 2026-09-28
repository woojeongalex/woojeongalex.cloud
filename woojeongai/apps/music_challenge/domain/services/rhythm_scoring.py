"""리듬 게임 판정·점수 규칙.

브라우저(alexview/lib/rhythm-scoring.ts)와 똑같은 규칙이다. 화면 점수는 조작할 수 있어
랭킹에는 서버가 입력 기록으로 다시 계산한 값만 쓴다. 한쪽을 고치면 반드시 둘 다 고친다.

- 판정 창: 노트 시각과의 차이 ±75ms COOL, ±130ms GOOD, ±185ms BAD. 밖이면 MISS.
  (2026-09-28 난이도를 낮추려고 60/110/160 에서 넓혔다.)
- 키를 누르면 그 레인에서 판정 창 안에 있는 가장 이른 미판정 노트를 친다.
  창 안에 노트가 없으면 아무 일도 없다(빈 누름에 벌점 없음).
- 롱노트는 머리와 꼬리를 따로 판정한다. 꼬리는 뗀 시각이 끝 시각보다 얼마나
  이르냐로 정하고, 끝까지 누르고 있었으면 COOL. 머리를 놓치면 꼬리도 MISS.
- 콤보: BAD·MISS 에서 끊긴다. 순서는 판정 기준 시각(머리=노트 시각, 꼬리=끝 시각).
- 점수(최대 1,000,000) = 900,000 × 정확도 + 100,000 × 최대 콤보 / 판정 수
  정확도 = (COOL + 0.6·GOOD + 0.2·BAD) / 판정 수
"""

from dataclasses import dataclass
from enum import Enum
from math import floor

from music_challenge.domain.value_objects.rhythm_vo import RhythmNote

COOL_WINDOW = 0.075
GOOD_WINDOW = 0.130
BAD_WINDOW = 0.185

MAX_SCORE = 1_000_000
_ACCURACY_PART = 900_000
_COMBO_PART = 100_000


class Judgement(str, Enum):
    COOL = "cool"
    GOOD = "good"
    BAD = "bad"
    MISS = "miss"


_WEIGHT = {
    Judgement.COOL: 1.0,
    Judgement.GOOD: 0.6,
    Judgement.BAD: 0.2,
    Judgement.MISS: 0.0,
}


@dataclass(frozen=True)
class Press:
    """키 한 번 누름. 시간은 곡 기준 초(지연 보정 후)."""

    lane: int
    down: float
    up: float


@dataclass(frozen=True)
class RhythmScore:
    score: int
    accuracy: float  # 0~100, 소수 둘째 자리
    max_combo: int
    cool: int
    good: int
    bad: int
    miss: int

    @property
    def total(self) -> int:
        return self.cool + self.good + self.bad + self.miss


def _round(x: float) -> int:
    """JS Math.round 와 같은 반올림. 파이썬 round 는 은행가 반올림이라 결과가 다르다."""
    return floor(x + 0.5)


def judge_offset(delta: float) -> Judgement:
    d = abs(delta)
    if d <= COOL_WINDOW:
        return Judgement.COOL
    if d <= GOOD_WINDOW:
        return Judgement.GOOD
    if d <= BAD_WINDOW:
        return Judgement.BAD
    return Judgement.MISS


def judge_release(up: float, end: float) -> Judgement:
    """롱노트 꼬리 — 끝 시각 이후까지 누르고 있었으면 COOL, 일찍 뗀 만큼 낮아진다."""
    return Judgement.COOL if up >= end else judge_offset(end - up)


def score_play(notes: list[RhythmNote], presses: list[Press]) -> RhythmScore:
    # (기준 시각, 레인, 꼬리 여부, 판정) — 콤보 순서를 정하는 데 쓴다.
    events: list[tuple[float, int, int, Judgement]] = []
    judged = [False] * len(notes)
    by_lane: dict[int, list[int]] = {}
    for i, note in enumerate(notes):
        by_lane.setdefault(note.lane, []).append(i)
    cursor = {lane: 0 for lane in by_lane}

    for press in sorted(presses, key=lambda p: (p.down, p.lane)):
        idxs = by_lane.get(press.lane)
        if not idxs:
            continue
        # 창을 이미 지나간 노트는 앞으로도 칠 수 없으므로 커서를 넘긴다.
        c = cursor[press.lane]
        while c < len(idxs) and (
            judged[idxs[c]] or notes[idxs[c]].time < press.down - BAD_WINDOW
        ):
            c += 1
        cursor[press.lane] = c
        if c >= len(idxs) or notes[idxs[c]].time > press.down + BAD_WINDOW:
            continue
        i = idxs[c]
        note = notes[i]
        judged[i] = True
        events.append((note.time, note.lane, 0, judge_offset(press.down - note.time)))
        if note.end is not None:
            events.append((note.end, note.lane, 1, judge_release(press.up, note.end)))

    for i, note in enumerate(notes):
        if not judged[i]:
            events.append((note.time, note.lane, 0, Judgement.MISS))
            if note.end is not None:
                events.append((note.end, note.lane, 1, Judgement.MISS))

    events.sort(key=lambda e: (e[0], e[1], e[2]))
    counts = {j: 0 for j in Judgement}
    combo = max_combo = 0
    for _, _, _, j in events:
        counts[j] += 1
        if j in (Judgement.COOL, Judgement.GOOD):
            combo += 1
            max_combo = max(max_combo, combo)
        else:
            combo = 0

    total = len(events)
    if total == 0:
        return RhythmScore(0, 0.0, 0, 0, 0, 0, 0)
    weighted = sum(_WEIGHT[j] * n for j, n in counts.items())
    score = _round(_ACCURACY_PART * weighted / total + _COMBO_PART * max_combo / total)
    return RhythmScore(
        score=min(MAX_SCORE, score),
        accuracy=_round(weighted / total * 10000) / 100,
        max_combo=max_combo,
        cool=counts[Judgement.COOL],
        good=counts[Judgement.GOOD],
        bad=counts[Judgement.BAD],
        miss=counts[Judgement.MISS],
    )
