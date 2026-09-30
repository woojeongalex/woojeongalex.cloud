from __future__ import annotations

from core.matrix.keymaker_api import get_keymaker
from music_challenge.app.ports.output.ai_chat_port import AiChatPort


class GeminiChatAdapter(AiChatPort):
    """API 키·모델은 항상 Keymaker 를 통해서만 얻는다 — 이 파일은 env 를 직접 읽지 않는다.

    예전에는 구글 검색 그라운딩을 켜 두었다. 날씨·최신 뉴스까지 답하게 하려던
    것인데, 이 화면은 "연습·음정·박자 질문"을 받는 자리라 실시간 정보가 필요
    없다. 그라운딩은 순수 생성과 **별도로** 요금과 할당량이 붙어서, 쓰지 않는
    기능에 계속 값을 치르고 있었다. 껐다.

    다시 켜야 하면 genai.protos.Tool(google_search_retrieval=...) 을 만들어
    generate_content 에 tools 로 넘기면 된다. 그때는 그라운딩 할당량만 따로
    터지는 경우(ResourceExhausted)를 잡아 검색 없이 재시도해야 한다.
    """

    def generate(self, message: str) -> str:
        model = get_keymaker().get_gemini_model()
        if model is None:
            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았습니다. backend/.env를 확인하세요."
            )

        try:
            response = model.generate_content(message)
        except Exception as e:
            raise RuntimeError(f"Gemini 호출 실패: {e}") from e

        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini가 빈 응답을 반환했습니다.")
        return text
