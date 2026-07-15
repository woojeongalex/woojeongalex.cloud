from __future__ import annotations

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from core.matrix.keymaker_api import Keymaker
from silicon_valley.app.ports.output.gemini_port import GeminiPort

# 날씨·최신 뉴스처럼 실시간 정보가 필요한 질문에도 답할 수 있도록 구글 검색
# 그라운딩을 켠다. 무료 티어는 이 기능에 별도의 훨씬 빡빡한 할당량이 있어
# 429(ResourceExhausted)가 날 수 있다 — 순수 생성 할당량과는 별개다.
_SEARCH_GROUNDING_TOOL = genai.protos.Tool(
    google_search_retrieval=genai.protos.GoogleSearchRetrieval()
)


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
            response = model.generate_content(message, tools=[_SEARCH_GROUNDING_TOOL])
        except ResourceExhausted:
            # 검색 그라운딩 할당량만 초과된 경우 -- 검색 없이 재시도해서
            # 최소한 일반 지식으로라도 답하게 한다.
            try:
                response = model.generate_content(message)
            except Exception as e:
                raise RuntimeError(f"Gemini 호출 실패: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Gemini 호출 실패: {e}") from e

        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini가 빈 응답을 반환했습니다.")
        return text
