from __future__ import annotations

from core.matrix.keymaker_api import Keymaker
from star_craft.app.ports.output.gemini_chat_port import GeminiChatPort


class GeminiChatGateway(GeminiChatPort):
    """Gemini로 자유 형식 질문에 답한다."""

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
            raise RuntimeError(f"Gemini 응답 실패: {e}") from e
        return (response.text or "").strip()
