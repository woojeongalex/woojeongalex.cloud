import base64
import json
import logging

from core.matrix.keymaker_api import get_keymaker
from music_challenge.app.ports.output.ai_evaluator_port import AIEvaluatorPort
from music_challenge.domain.value_objects.music_challenge_vo import (
    ChallengeType,
    MediaType,
)

logger = logging.getLogger(__name__)

_MAX_INLINE_BYTES = 20 * 1024 * 1024  # 20MB


class GeminiEvaluatorAdapter(AIEvaluatorPort):
    async def evaluate(
        self,
        challenge_title: str,
        challenge_description: str,
        challenge_type: ChallengeType,
        media_bytes: bytes,
        media_type: MediaType,
        content_type: str,
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
                f"제출된 {media_type.value} 파일을 듣고 아래 기준으로 평가하세요:\n"
                f"- 정확도 (음정·박자·리듬)\n"
                f"- 표현력과 감정\n"
                f"- 전체 완성도\n\n"
                f'반드시 JSON으로만 응답: {{"score": 0~100 정수, "feedback": "한국어 피드백 2~3문장"}}'
            )

            response = model.generate_content(
                [
                    {"mime_type": content_type, "data": b64},
                    prompt,
                ]
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
