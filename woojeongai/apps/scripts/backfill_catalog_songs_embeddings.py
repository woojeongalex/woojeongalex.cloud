# ruff: noqa: E402
"""catalog_songs.embedding 일괄 채우기: python scripts/backfill_catalog_songs_embeddings.py

로컬 EXAONE 임베딩 서버(vLLM --runner pooling --convert embed)를 호출한다.
서버가 채팅 모드가 아니라 임베딩 모드로 떠 있어야 한다.
"""

import asyncio
import os
import sys
from pathlib import Path

_APPS_DIR = Path(__file__).resolve().parent.parent
_BACKEND_DIR = _APPS_DIR.parent
for _path in (_BACKEND_DIR, _APPS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
from dotenv import load_dotenv

load_dotenv(_BACKEND_DIR / ".env")

EMBED_MODEL = os.getenv("LOCAL_LLM_MODEL") or "EXAONE-3.5-7.8B-Instruct-AWQ"


def embed_text(base_url: str, text_input: str) -> list[float]:
    import requests

    response = requests.post(
        f"{base_url}/v1/embeddings",
        json={"model": EMBED_MODEL, "input": text_input},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


async def main() -> int:
    base_url = (os.getenv("LOCAL_LLM_BASE_URL") or "").rstrip("/")
    if not base_url:
        print("FAIL: LOCAL_LLM_BASE_URL 없음 (backend/.env)")
        return 1

    from sqlalchemy import text

    from database import dispose_engine, get_session_factory, init_db

    await init_db()
    factory = get_session_factory()

    async with factory() as session:
        rows = (
            await session.execute(
                text(
                    "SELECT catalog_song_id, title, artist, mr_description"
                    " FROM catalog_songs WHERE embedding IS NULL"
                )
            )
        ).fetchall()
        print(f"embedding 없는 곡 {len(rows)}개")

        for row in rows:
            song_id, title, artist, mr_description = row
            combined = " ".join(p for p in (title, artist, mr_description) if p)
            vector = embed_text(base_url, combined)
            await session.execute(
                text(
                    "UPDATE catalog_songs SET embedding = :v WHERE catalog_song_id = :id"
                ),
                {"v": str(vector), "id": song_id},
            )
            print(f"embedded {song_id}: {title}")

        await session.commit()

    await dispose_engine()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
