from __future__ import annotations

from core.matrix.keymaker_api import Keymaker
from silicon_valley.app.ports.output.gemini_port import GeminiPort


class GeminiClient(GeminiPort):
    """Gemini 호출 어댑터. API 키·모델은 항상 Keymaker를 통해서만 얻는다 —
    이 파일은 env 변수를 직접 읽지 않는다."""

    def __init__(self, keymaker: Keymaker):
        self._keymaker = keymaker

    def generate(self, message: str) -> str:
        if not self._keymaker.is_gemini_ready():
            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았습니다. backend/.env를 확인하세요."
            )

        model = self._keymaker.get_gemini_model()
        try:
            response = model.generate_content(message)
        except Exception as e:
            raise RuntimeError(f"Gemini 호출 실패: {e}") from e

        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini가 빈 응답을 반환했습니다.")
        return text
