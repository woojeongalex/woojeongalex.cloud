import base64
import json
import logging

from core.matrix.keymaker_api import get_keymaker
from music_challenge.app.ports.output.ai_evaluator_port import AIEvaluatorPort
from music_challenge.app.ports.output.audio_analysis_port import AudioMetrics
from music_challenge.domain.services.karaoke_scoring import KaraokeScore
from music_challenge.domain.services.vocal_traits import VocalTraits
from music_challenge.domain.value_objects.music_challenge_vo import (
    ChallengeType,
    MediaType,
)

logger = logging.getLogger(__name__)

_MAX_INLINE_BYTES = 20 * 1024 * 1024  # 20MB

# 같은 제출에 매번 다른 점수가 나오면 랭킹을 붙일 수 없다. 샘플링을 끄고
# JSON 만 받는다.
_GENERATION_CONFIG = {
    "temperature": 0.0,
    "response_mime_type": "application/json",
}

# 점수 기준을 명시하지 않으면 모델이 매번 다른 잣대를 쓴다.
_RUBRIC = """점수 기준(반드시 따를 것):
- 90~100: 음정·박자가 모두 안정적이고 표현력까지 뛰어남
- 70~89 : 대체로 안정적이나 일부 구간이 흔들림
- 50~69 : 기본은 갖췄으나 뚜렷한 개선점이 있음
- 30~49 : 음정 또는 박자가 전반적으로 불안정함
- 0~29  : 노래나 연주로 보기 어려움(무음, 잡음, 테스트 신호음 등)"""


def _metrics_block(metrics: AudioMetrics | None) -> str:
    if metrics is None:
        return "객관 지표: 분석 불가(영상이거나 디코딩할 수 없는 형식). 오디오만으로 판단하세요."
    return (
        "객관 지표(신호 분석으로 측정된 값이므로 반드시 근거로 삼을 것):\n"
        f"- 음정 안정성: {metrics.pitch_score}/100 "
        f"(평균 {metrics.mean_hz:.1f}Hz, 표준편차 {metrics.std_hz:.1f}Hz)\n"
        f"- 박자 일관성: {metrics.rhythm_score}/100\n"
        f"- 템포: {metrics.tempo:.1f}BPM · 길이: {metrics.duration:.1f}초\n"
        "주의: 이 수치는 '안정성'만 재므로 기계적으로 일정한 신호음도 높게 나온다. "
        "실제 사람의 가창·연주인지는 오디오를 직접 듣고 판단하세요."
    )


def _karaoke_block(karaoke: KaraokeScore | None) -> str:
    if karaoke is None:
        return ""
    return (
        "\n\n노래방·연주 채점 결과(원곡의 정답 음표와 녹음을 맞춰 본 값 — 가장 중요한 근거):\n"
        f"- 정답 음과 일치한 비율: {karaoke.pitch_accuracy}%\n"
        f"- 음표를 제때 시작한 비율: {karaoke.timing_accuracy}%\n"
        f"- 종합: {karaoke.score}/100\n"
        "피드백은 이 두 수치 중 낮은 쪽을 먼저 짚고, 다음 도전에서 바로 해 볼 수 있는 "
        "구체적인 연습 방법 하나를 제안하세요."
    )


def _midi_name(midi: float) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    n = int(round(midi))
    return f"{names[n % 12]}{n // 12 - 1}"


def _traits_block(traits: VocalTraits | None) -> str:
    """발성 진단을 모델이 읽을 문장으로. 잰 항목만 넣는다 — 없는 값을 채우면
    모델이 지어낸다."""
    if traits is None:
        return ""

    lines: list[str] = []
    if traits.voiced_ratio < 85:
        lines.append(
            f"- 음표 구간의 {traits.voiced_ratio}% 에서만 소리가 났다"
            "(나머지는 쉬었거나 소리가 끊겼다)"
        )
    if traits.pitch_bias_cents is not None and abs(traits.pitch_bias_cents) >= 15:
        쪽 = "높게" if traits.pitch_bias_cents > 0 else "낮게"
        lines.append(
            f"- 음정이 평균적으로 {abs(traits.pitch_bias_cents)}센트 {쪽} 치우쳤다"
        )
    if traits.flat_ratio is not None and traits.flat_ratio >= 65:
        lines.append(f"- 음이 어긋난 순간의 {traits.flat_ratio}% 가 아래로 쳐진 것이다")
    elif traits.flat_ratio is not None and traits.flat_ratio <= 35:
        lines.append(
            f"- 음이 어긋난 순간의 {100 - traits.flat_ratio}% 가 위로 뜬 것이다"
        )
    if traits.attack_delay_ms is not None and traits.attack_delay_ms >= 120:
        lines.append(
            f"- 음을 제 음높이로 잡기까지 중앙값 {traits.attack_delay_ms}ms 걸렸다"
        )
    if traits.low_accuracy is not None and traits.high_accuracy is not None:
        gap = traits.high_accuracy - traits.low_accuracy
        if abs(gap) >= 10:
            약 = "높은" if gap < 0 else "낮은"
            lines.append(
                f"- 낮은 음 구간 {traits.low_accuracy}% / 높은 음 구간 "
                f"{traits.high_accuracy}% — {약} 쪽에서 더 무너진다"
            )
    if traits.vibrato_extent_cents is not None and traits.vibrato_rate_hz is not None:
        lines.append(
            f"- 긴 음의 흔들림 폭 {traits.vibrato_extent_cents}센트 · "
            f"속도 {traits.vibrato_rate_hz}Hz "
            "(5~7Hz·20~100센트면 비브라토, 그보다 느리고 넓으면 음정이 불안한 것)"
        )
    if traits.comfort_low_midi is not None and traits.comfort_high_midi is not None:
        lines.append(
            f"- 편하게 낸 음역은 {_midi_name(traits.comfort_low_midi)}"
            f"~{_midi_name(traits.comfort_high_midi)} 였다"
        )
    if traits.weak_note_count:
        lines.append(f"- 절반도 못 맞힌 음표가 {traits.weak_note_count}개 있다")

    if not lines:
        return ""
    return (
        "\n\n발성 진단(같은 녹음의 음높이 곡선에서 측정한 값):\n"
        + "\n".join(lines)
        + "\n이 중 가장 두드러진 하나를 골라 왜 그렇게 들리는지와 "
        "바로 해 볼 연습을 말하세요. 잰 적 없는 것(호흡량, 성대 상태, 발음, "
        "감정)은 단정하지 마세요."
    )


class GeminiEvaluatorAdapter(AIEvaluatorPort):
    async def evaluate(
        self,
        challenge_title: str,
        challenge_description: str,
        challenge_type: ChallengeType,
        media_bytes: bytes,
        media_type: MediaType,
        content_type: str,
        metrics: AudioMetrics | None = None,
        karaoke: KaraokeScore | None = None,
        traits: VocalTraits | None = None,
    ) -> tuple[int, str]:
        try:
            # 모델명을 하드코딩하면 모델이 폐기될 때 조용히 404가 난다(실제로
            # gemini-1.5-flash 가 그렇게 죽었다). 저장소 표준대로 Keymaker 가
            # .env 의 GEMINI_MODEL 을 읽어 만든 모델을 재사용한다.
            model = get_keymaker().get_gemini_model()
            if model is None:
                logger.warning("Gemini 모델 미설정 — GEMINI_API_KEY 를 확인하세요")
                return 70, "AI 평가를 사용할 수 없어 기본 점수를 부여합니다."

            if len(media_bytes) > _MAX_INLINE_BYTES:
                return (
                    65,
                    f"파일 크기 초과로 자동 분석이 제한되었습니다. [{challenge_title}] 챌린지 참여 감사합니다!",
                )

            b64 = base64.b64encode(media_bytes).decode()
            prompt = (
                f"당신은 음악 챌린지 평가 전문가입니다.\n"
                f"챌린지명: [{challenge_title}]\n"
                f"설명: {challenge_description}\n"
                f"유형: {challenge_type.value} (vocal=노래, instrument=악기, both=둘 다)\n\n"
                # 노래방 모드는 일반 지표를 일부러 건너뛴다(정답 대비 결과가 더 정확하다).
                # 그때 "분석 불가"라고 쓰면 모델이 오디오가 깨진 줄 안다.
                f"{'' if karaoke and metrics is None else _metrics_block(metrics)}"
                f"{_karaoke_block(karaoke)}"
                f"{_traits_block(traits)}\n\n"
                f"{_RUBRIC}\n\n"
                f"제출된 {media_type.value} 파일을 듣고 정확도(음정·박자·리듬), "
                f"표현력과 감정, 전체 완성도를 평가하세요.\n"
                f'반드시 JSON으로만 응답: {{"score": 0~100 정수, "feedback": "한국어 피드백 2~3문장"}}'
            )

            response = model.generate_content(
                [
                    {"mime_type": content_type, "data": b64},
                    prompt,
                ],
                generation_config=_GENERATION_CONFIG,
            )
            return self._parse(response.text)
        except Exception as e:
            logger.warning("Gemini 평가 실패: %s", e)
            return 70, "평가 중 오류가 발생했습니다. 기본 점수를 부여합니다."

    def _parse(self, text: str) -> tuple[int, str]:
        try:
            cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
            data = json.loads(cleaned)
            score = max(0, min(100, int(data.get("score", 70))))
            feedback = str(data.get("feedback", "평가 완료"))
            return score, feedback
        except Exception:
            return 70, text[:500] if text else "평가 결과를 처리할 수 없습니다."
