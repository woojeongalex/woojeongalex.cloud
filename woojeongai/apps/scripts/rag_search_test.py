# ruff: noqa: E402
"""RAG 1단계(검색) 수동 테스트: vLLM이 임베딩 모드일 때 실행.

사용법: docker compose exec backend python3 apps/scripts/rag_search_test.py "질문"

질문을 임베딩하고 catalog_songs에서 가장 가까운 곡을 검색해 출력한다.
결과는 2단계(rag_answer_test.py)가 이어서 쓸 수 있도록 캐시 파일에 저장한다.
"""

import asyncio
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


async def main() -> int:
    if len(sys.argv) < 2:
        print('사용법: python3 rag_search_test.py "질문"')
        return 1
    query = sys.argv[1]

    from core.matrix import database_manager
    from core.matrix.local_llm_client import get_local_llm_client
    from silicon_valley.adapter.outbound.repositories.song_rag_repository import (
        SongRagRepository,
    )

    client = get_local_llm_client()
    if not client.is_embed_ready():
        print("FAIL: LOCAL_LLM_EMBED_BASE_URL 없음 (backend/.env)")
        return 1

    print(f"질문: {query}")
    vector = client.embed(query)
    print(f"임베딩 완료 ({len(vector)}차원)")

    database_manager.init_engine()
    async with database_manager.async_session_factory() as session:
        repo = SongRagRepository(session=session)
        songs = await repo.search_similar_songs(vector, limit=3)
    await database_manager.dispose_engine()

    print("\n검색된 곡:")
    for song in songs:
        print(f"- {song['title']} ({song['artist']}): {song['mr_description']}")

    CACHE_PATH.write_text(
        json.dumps({"query": query, "songs": songs}, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n캐시 저장됨: {CACHE_PATH.name} (2단계에서 자동으로 읽음)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
