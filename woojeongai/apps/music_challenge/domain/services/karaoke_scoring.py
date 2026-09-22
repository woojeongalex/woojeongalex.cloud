"""노래방·연주 채점 — 정답 음표 대비 음정·박자.

브라우저의 실시간 채점(alexview/lib/karaoke-scoring.ts)과 같은 규칙이다.
화면 점수는 조작할 수 있으므로 랭킹에는 이 서버 점수만 쓴다. 한쪽 값을 바꾸면
다른 쪽도 같이 바꿔야 화면 점수와 최종 점수가 크게 어긋나지 않는다.

- 옥타브는 따지지 않는다(남자가 여자 노래를 한 옥타브 낮게 불러도 정답).
- 음정: ±50센트 안이면 온전히, ±100센트 안이면 절반만 인정한다.
- 박자: 음표가 시작되고 0.2초 안에 맞는 음을 내기 시작하면 제때 들어간 것이다.
- 음표 점수 = 음정 75% + 박자 25%. 긴 음표일수록 전체 점수에 크게 반영된다.
"""

import math
from dataclasses import dataclass

from music_challenge.domain.value_objects.chart_vo import Note

PERFECT_CENTS = 50
GOOD_CENTS = 100
TIMING_WINDOW_SEC = 0.2
_PITCH_WEIGHT = 0.75
_TIMING_WEIGHT = 0.25
_MAX_FRAME_SEC = 0.1
# 음표 경계에서 빠지는 프레임을 봐주는 폭 — 30fps 에서 두 프레임
_FRAME_SLACK_SEC = 1 / 30


@dataclass(frozen=True)
class KaraokeScore:
    score: int
    pitch_accuracy: int
    timing_accuracy: int


def _round(x: float) -> int:
    """JS Math.round 와 같게 .5 는 올린다. 파이썬 round 는 짝수 쪽으로 보내서
    (round(62.5) == 62) 화면 점수와 1점씩 어긋난다."""
    return int(math.floor(x + 0.5))


def folded_semitones(user_midi: float, target_midi: float) -> float:
    """옥타브를 접은 음정 차이(반음). -6 이상 6 미만."""
    return (((user_midi - target_midi) % 12) + 18) % 12 - 6


@dataclass
class _Progress:
    hit: float = 0.0
    elapsed: float = 0.0
    onset_delay: float | None = None


def score_performance(
    notes: list[Note], frames: list[tuple[float, float | None]]
) -> KaraokeScore:
    """frames 는 (곡 기준 초, MIDI 음높이 또는 None) 을 시간순으로 담는다."""
    if not notes:
        return KaraokeScore(score=0, pitch_accuracy=0, timing_accuracy=0)

    progress = [_Progress() for _ in notes]
    cursor = 0
    last_time: float | None = None

    for t, midi in frames:
        dt = 0.0 if last_time is None else min(_MAX_FRAME_SEC, max(0.0, t - last_time))
        last_time = t
        while cursor < len(notes) and t >= notes[cursor].end:
            cursor += 1
        if cursor >= len(notes):
            break
        note = notes[cursor]
        if t < note.start or dt == 0:
            continue
        p = progress[cursor]
        p.elapsed += dt
        if midi is None:
            continue
        cents = abs(folded_semitones(midi, note.midi)) * 100
        credit = 1.0 if cents <= PERFECT_CENTS else 0.5 if cents <= GOOD_CENTS else 0.0
        if credit > 0:
            p.hit += dt * credit
            if p.onset_delay is None:
                p.onset_delay = t - note.start

    weighted = pitch_weighted = total = 0.0
    on_time = 0
    for note, p in zip(notes, progress):
        duration = note.end - note.start
        denom = max(p.elapsed, duration - _FRAME_SLACK_SEC)
        pitch_ratio = min(1.0, p.hit / denom) if denom > 0 else 0.0
        timely = p.onset_delay is not None and p.onset_delay <= TIMING_WINDOW_SEC
        points = _PITCH_WEIGHT * pitch_ratio + _TIMING_WEIGHT * (1.0 if timely else 0.0)
        weighted += points * duration
        pitch_weighted += pitch_ratio * duration
        total += duration
        on_time += 1 if timely else 0

    return KaraokeScore(
        score=_round(100 * weighted / total) if total > 0 else 0,
        pitch_accuracy=_round(100 * pitch_weighted / total) if total > 0 else 0,
        timing_accuracy=_round(100 * on_time / len(notes)),
    )
