"""잰 값으로 점수와 코칭을 만드는 평가 어댑터 — 외부 호출이 없다.

예전에는 Gemini 가 이 자리를 맡았다. 걷어낸 이유:

- **돈.** 제출마다 녹음을 통째로 올렸다. 4분짜리 곡이면 요청 하나가 9.8MB 다.
- **지어냄.** 녹음을 주면 "표현력이 좋습니다" 처럼 재지 않은 것을 말했다.
- **흔들림.** 같은 파일에 0~70점이 나오던 시절이 있었고, 그래서 이미 점수는
  정답 대비 결정적인 값으로 덮어쓰고 있었다. 모델이 하는 일은 문장뿐이었다.

지금은 음정·박자·발성을 전부 숫자로 재 놓았으므로 그 숫자에서 바로 쓴다.
같은 입력이면 같은 문장이 나온다.

다시 LLM 을 붙이고 싶으면 이 자리에 다른 어댑터를 넣으면 된다 — 포트는
그대로다.
"""

from __future__ import annotations

from music_challenge.app.ports.output.ai_evaluator_port import AIEvaluatorPort
from music_challenge.app.ports.output.audio_analysis_port import AudioMetrics
from music_challenge.domain.services.karaoke_scoring import KaraokeScore
from music_challenge.domain.services.vocal_coaching import coach_karaoke, coach_metrics
from music_challenge.domain.services.vocal_traits import VocalTraits
from music_challenge.domain.value_objects.music_challenge_vo import (
    ChallengeType,
    MediaType,
)


class RuleBasedEvaluatorAdapter(AIEvaluatorPort):
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
        if karaoke is not None:
            result = coach_karaoke(karaoke, traits)
        else:
            result = coach_metrics(
                pitch_score=metrics.pitch_score if metrics else None,
                rhythm_score=metrics.rhythm_score if metrics else None,
                duration=metrics.duration if metrics else None,
            )
        return result.score, result.feedback
