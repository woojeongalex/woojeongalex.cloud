# ruff: noqa: E402
"""RAG 2단계(답변) 수동 테스트: vLLM이 채팅 모드일 때 실행.

사용법: docker compose exec backend python3 apps/scripts/rag_answer_test.py

rag_search_test.py가 저장해둔 캐시(질문 + 검색된 곡)를 읽어 Hendricks
페르소나로 최종 답변을 생성한다.
"""

import json
import sys
from pathlib import Path

_APPS_DIR = Path(__file__).resolve().parent.parent
_BACKEND_DIR = _APPS_DIR.parent
for _path in (_BACKEND_DIR, _APPS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
from dotenv import load_dotenv

load_dotenv(_BACKEND_DIR / ".env")

CACHE_PATH = Path(__file__).resolve().parent / ".rag_test_cache.json"


def main() -> int:
    if not CACHE_PATH.exists():
        print("FAIL: 캐시 파일이 없습니다. 먼저 rag_search_test.py를 실행하세요.")
        return 1
    cached = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    query = cached["query"]
    songs = cached["songs"]

    from core.matrix.local_llm_client import get_local_llm_client
    from silicon_valley.app.use_cases.piper_hendricks__ceo_interactor import (
        _format_song_context,
    )
    from silicon_valley.domain.constants.piper_personas import (
        HENDRICKS_CEO_SYSTEM_PROMPT,
    )

    client = get_local_llm_client()
    if not client.is_ready():
        print("FAIL: LOCAL_LLM_BASE_URL 없음 (backend/.env)")
        return 1

    context = _format_song_context(songs)
    system_prompt = (
        f"{HENDRICKS_CEO_SYSTEM_PROMPT}\n\n{context}"
        if context
        else HENDRICKS_CEO_SYSTEM_PROMPT
    )

    print(f"질문: {query}")
    print(f"참고한 곡: {', '.join(s['title'] for s in songs)}")
    reply = client.generate(query, system_prompt)
    print(f"\n답변: {reply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
