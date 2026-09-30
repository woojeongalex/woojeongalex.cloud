"""코칭 문장 — 잰 값에서 규칙으로 만든다.

예전에는 Gemini 가 썼다. 두 가지가 문제였다. 하나는 제출마다 요금이 나갔고,
둘은 녹음을 주면 "표현력이 좋습니다" 처럼 재지 않은 것을 지어냈다.

지금은 음정·박자·발성을 전부 숫자로 재 놓았으므로 그 숫자에서 바로 쓴다.
같은 입력이면 같은 문장이 나오고, 재지 않은 것은 절대 말하지 않는다.

쓰는 방식은 하나다 — **가장 크게 무너진 것 하나를 골라** 무엇이 어떻게
일어났는지 말하고, 바로 해 볼 연습 하나를 준다. 여러 개를 나열하면 무엇부터
할지 알 수 없어 아무것도 안 하게 된다.
"""

from __future__ import annotations

from dataclasses import dataclass

from music_challenge.domain.services.karaoke_scoring import KaraokeScore
from music_challenge.domain.services.vocal_traits import VocalTraits

# 이 아래면 그 항목이 무너진 것으로 본다.
_VOICED_LOW = 75
_TIMING_LOW = 80
_PITCH_LOW = 85
_FLAT_HEAVY = 65
_RANGE_GAP = 15
_BIAS_LARGE = 25
_ATTACK_SLOW = 120
# 비브라토로 볼 범위. 밖이면 흔들림이다.
_VIB_RATE = (4.5, 7.5)
_VIB_EXTENT = (20, 100)


@dataclass(frozen=True)
class Coaching:
    score: int
    feedback: str


def _praise(karaoke: KaraokeScore) -> str:
    if karaoke.score >= 95:
        return (
            f"음정 {karaoke.pitch_accuracy}% · 박자 {karaoke.timing_accuracy}% 로 "
            "흠잡을 데가 없습니다. 같은 곡을 한 음 높여 부르거나, 음역이 더 넓은 "
            "곡으로 옮겨 볼 때입니다."
        )
    return (
        f"음정 {karaoke.pitch_accuracy}% · 박자 {karaoke.timing_accuracy}% 로 "
        "고르게 불렀습니다. 지금 흐름을 유지하면서, 긴 음을 끝까지 같은 세기로 "
        "밀어 보는 연습을 더해 보세요."
    )


def _weakest(karaoke: KaraokeScore, traits: VocalTraits | None) -> str | None:
    """가장 크게 무너진 것 하나. 다 괜찮으면 None."""
    if traits is not None and traits.voiced_ratio < _VOICED_LOW:
        return (
            f"음표 구간의 {traits.voiced_ratio}% 에서만 소리가 났습니다. "
            "음을 맞히기 전에 먼저 끊기지 않게 부르는 것이 순서입니다. "
            "가사를 보지 않고 흥얼거리며 한 소절을 끝까지 이어 보세요."
        )

    if karaoke.timing_accuracy < _TIMING_LOW:
        late = ""
        if traits is not None and traits.attack_delay_ms is not None:
            late = f" 음을 잡기까지 평균 {traits.attack_delay_ms}ms 가 걸립니다."
        return (
            f"음표를 제때 시작한 비율이 {karaoke.timing_accuracy}% 입니다.{late} "
            "박자는 음정보다 먼저 잡아야 합니다. 반주만 틀어 놓고 "
            "각 소절의 첫 글자에 손뼉을 쳐 보세요."
        )

    if karaoke.pitch_accuracy >= _PITCH_LOW or traits is None:
        return None

    if (
        traits.low_accuracy is not None
        and traits.high_accuracy is not None
        and abs(traits.low_accuracy - traits.high_accuracy) >= _RANGE_GAP
    ):
        high_weak = traits.high_accuracy < traits.low_accuracy
        쪽 = "높은 음" if high_weak else "낮은 음"
        조언 = (
            "높은 음은 더 세게 내려 할수록 더 눌립니다. 소리를 위로 띄운다는 "
            "느낌으로, 편한 음역에서 반음씩 올려 가며 같은 세기를 유지해 보세요."
            if high_weak
            else "낮은 음은 힘을 빼야 울립니다. 턱과 혀에 힘을 빼고 "
            "낮은 음에서 시작해 반음씩 내려가 보세요."
        )
        return (
            f"낮은 음 {traits.low_accuracy}% · 높은 음 {traits.high_accuracy}% 로 "
            f"{쪽}에서 더 무너집니다. {조언}"
        )

    if traits.flat_ratio is not None and traits.flat_ratio >= _FLAT_HEAVY:
        return (
            f"음이 어긋난 순간의 {traits.flat_ratio}% 가 아래로 쳐진 것입니다. "
            "쳐지는 것은 대개 숨이 모자라서입니다. 한 소절을 부르기 전에 숨을 "
            "충분히 채우고, 소절 끝까지 세기가 줄지 않게 밀어 보세요."
        )

    if traits.pitch_bias_cents is not None and abs(traits.pitch_bias_cents) >= _BIAS_LARGE:
        쪽 = "높게" if traits.pitch_bias_cents > 0 else "낮게"
        return (
            f"음정이 평균적으로 {abs(traits.pitch_bias_cents)}센트 {쪽} 치우쳐 "
            "있습니다. 한쪽으로 쏠린 것은 귀보다 습관의 문제라, 튜너나 피아노로 "
            "한 음을 길게 내며 바늘이 가운데 서는 감각을 먼저 잡아야 합니다."
        )

    if traits.attack_delay_ms is not None and traits.attack_delay_ms >= _ATTACK_SLOW:
        return (
            f"음을 제 높이로 잡기까지 {traits.attack_delay_ms}ms 가 걸립니다. "
            "첫 소리를 더듬어 찾고 있다는 뜻입니다. 부르기 전에 그 음을 속으로 "
            "먼저 그려 보고 내는 연습을 해 보세요."
        )

    if traits.vibrato_extent_cents is not None and traits.vibrato_rate_hz is not None:
        steady = (
            _VIB_RATE[0] <= traits.vibrato_rate_hz <= _VIB_RATE[1]
            and _VIB_EXTENT[0] <= traits.vibrato_extent_cents <= _VIB_EXTENT[1]
        )
        if not steady:
            return (
                f"긴 음이 {traits.vibrato_extent_cents}센트 폭으로 "
                f"{traits.vibrato_rate_hz}Hz 에서 흔들립니다. 비브라토라기보다 "
                "음정이 버티지 못하는 쪽에 가깝습니다. 긴 음을 흔들지 말고 "
                "일자로 끝까지 버티는 연습부터 해 보세요."
            )

    return (
        f"정답 음과 일치한 비율이 {karaoke.pitch_accuracy}% 입니다. "
        "반주를 작게 틀고 느린 속도로 한 소절씩 따라 부르며 "
        "음을 정확히 짚는 연습이 먼저입니다."
    )


def coach_karaoke(karaoke: KaraokeScore, traits: VocalTraits | None) -> Coaching:
    """노래방·연주 제출의 코칭. 점수는 이미 정해져 있으므로 문장만 만든다."""
    weak = _weakest(karaoke, traits)
    return Coaching(score=karaoke.score, feedback=weak or _praise(karaoke))


# 정답 악보가 없을 때 쓰는 가중치. 음정을 더 본다.
_PITCH_WEIGHT, _RHYTHM_WEIGHT = 0.6, 0.4
# 악보도 없고 분석도 안 되면(영상 등) 줄 점수. 참여는 했으므로 0 은 아니다.
_NO_EVIDENCE_SCORE = 70


def coach_metrics(
    pitch_score: int | None, rhythm_score: int | None, duration: float | None
) -> Coaching:
    """정답 악보가 없는 제출 — librosa 가 잰 안정성만으로 판단한다.

    이 값들은 "정답에 맞았나"가 아니라 "흔들림이 적었나"만 잰다. 기계적으로
    일정한 신호음도 높게 나오므로, 문장에서 잘 불렀다고 단정하지 않는다.
    """
    if pitch_score is None or rhythm_score is None:
        return Coaching(
            score=_NO_EVIDENCE_SCORE,
            feedback=(
                "이 제출은 오디오를 분석할 수 없어 점수를 자세히 내지 못했습니다. "
                "음정·박자를 재려면 노래방 모드로, 소리만 담긴 파일로 올려 주세요."
            ),
        )

    score = round(_PITCH_WEIGHT * pitch_score + _RHYTHM_WEIGHT * rhythm_score)
    length = f" 길이는 {duration:.0f}초입니다." if duration else ""

    if pitch_score < rhythm_score - 10:
        tip = (
            f"음높이가 {pitch_score}점으로 박자({rhythm_score}점)보다 많이 흔들립니다. "
            "긴 음을 일자로 버티는 연습이 먼저입니다."
        )
    elif rhythm_score < pitch_score - 10:
        tip = (
            f"박자가 {rhythm_score}점으로 음높이({pitch_score}점)보다 흔들립니다. "
            "메트로놈에 맞춰 같은 구절을 반복해 보세요."
        )
    else:
        tip = f"음높이 {pitch_score}점 · 박자 {rhythm_score}점으로 고르게 유지했습니다."

    return Coaching(
        score=score,
        feedback=(
            f"{tip}{length} 이 수치는 흔들림이 적은지만 재므로, 정답 음과 "
            "얼마나 맞았는지는 노래방 모드에서 확인할 수 있습니다."
        ),
    )
