from __future__ import annotations

import json
import logging
import re

from core.matrix.keymaker_api import Keymaker
from star_craft.app.ports.output.keyword_parser_port import KeywordParserPort

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = (
    "다음은 웹페이지에서 무언가를 찾아달라는 사용자의 자연어 요청이다. "
    "여기서 실제로 페이지 텍스트를 검색할 핵심 키워드(짧은 단어나 구)를 하나만 뽑아라. "
    "특정 주제어로 필터링하려는 게 아니라 순위표·목록 전체(예: '1위부터 100위까지', "
    "'전체 목록', '다 가져와')를 수집하려는 요청이면 keyword를 빈 문자열(\"\")로 답하라. "
    "반드시 아래 JSON 형식으로만 답하고 다른 설명은 붙이지 마라:\n"
    '{{"keyword": "..."}}\n\n'
    "요청: {command}"
)

_JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


class GeminiKeywordParser(KeywordParserPort):
    """Gemini로 자연어 요청에서 검색 키워드를 추출한다."""

    def __init__(self, keymaker: Keymaker):
        self._keymaker = keymaker

    def extract_keyword(self, command: str) -> str:
        if not self._keymaker.is_gemini_ready():
            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았습니다. backend/.env를 확인하세요."
            )

        model = self._keymaker.get_gemini_model()
        try:
            response = model.generate_content(_PROMPT_TEMPLATE.format(command=command))
        except Exception as e:
            raise RuntimeError(f"명령 해석 실패: {e}") from e

        text = (response.text or "").strip()
        match = _JSON_PATTERN.search(text)
        if not match:
            raise RuntimeError(
                "명령에서 키워드를 이해하지 못했습니다. 다시 말씀해 주세요."
            )

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            raise RuntimeError("명령 해석 결과가 올바른 형식이 아닙니다.") from e

        keyword = str(data.get("keyword", "")).strip()
        logger.info(
            f"[GeminiKeywordParser] 명령='{command}' → 키워드='{keyword or '(전체 수집)'}'"
        )
        return keyword
