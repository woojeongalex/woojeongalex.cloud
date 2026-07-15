# ruff: noqa: E402
"""music_mood_recommendations.jsonl에서 깨진 예시를 걸러내고 N개로 줄인다.

python3 filter_music_qlora_dataset.py [남길 개수(기본 30)]
"""

import asyncio
import json
import re
import sys
from pathlib import Path

_APPS_DIR = Path(__file__).resolve().parent.parent
_BACKEND_DIR = _APPS_DIR.parent
for _path in (_BACKEND_DIR, _APPS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

DATA_PATH = (
    Path(__file__).resolve().parent / "qlora_data" / "music_mood_recommendations.jsonl"
)

# 한글 바로 옆에 공백 없이 영문 2글자 이상이 붙은 경우 (예: "지치고ograft") = 깨진 토큰
_GARBLED_PATTERN = re.compile(r"[가-힣][a-zA-Z]{2,}|[a-zA-Z]{2,}[가-힣]")
_KOREAN_PATTERN = re.compile(r"[가-힣]")
_LATIN_PATTERN = re.compile(r"[a-zA-Z]")

# 답변은 곡 추천 이유를 설명하는 한국어 문장이어야 하므로, 한글 비중이 너무
# 낮으면(예: " isometric" 같은 영단어 하나만 남은 응답, 영어 문장이 섞인 응답) 깨진 것으로 간주한다.
_MIN_LEN = {"user": 3, "assistant": 15}
_MIN_KOREAN_CHARS_ASSISTANT = 10
_MIN_KOREAN_RATIO_ASSISTANT = 0.5


async def fetch_song_catalog() -> list[tuple[str, str]]:
    from sqlalchemy import text

    from core.matrix import database_manager

    database_manager.init_engine()
    async with database_manager.async_session_factory() as session:
        rows = (
            await session.execute(
                text(
                    "SELECT title, artist FROM catalog_songs"
                    " WHERE title IS NOT NULL AND artist IS NOT NULL"
                )
            )
        ).fetchall()
    await database_manager.dispose_engine()
    return [(row[0], row[1]) for row in rows]


def is_clean(example: dict, known_titles: set[str]) -> bool:
    assistant_mentions_known_song = False
    for msg in example["messages"]:
        content = msg["content"].strip()
        role = msg["role"]
        if _GARBLED_PATTERN.search(content):
            return False
        if len(content) < _MIN_LEN.get(role, 3):
            return False
        if role == "assistant":
            korean_chars = len(_KOREAN_PATTERN.findall(content))
            latin_chars = len(_LATIN_PATTERN.findall(content))
            if korean_chars < _MIN_KOREAN_CHARS_ASSISTANT:
                return False
            if latin_chars and korean_chars / (korean_chars + latin_chars) < _MIN_KOREAN_RATIO_ASSISTANT:
                return False
            if any(title in content for title in known_titles):
                assistant_mentions_known_song = True
    # DB에 실제 존재하는 곡 목록이 있다면, 답변이 그중 하나를 실제로 언급해야
    # 한다 — 그렇지 않으면 지어낸(환각) 곡/가수일 가능성이 높다.
    return not known_titles or assistant_mentions_known_song


async def main() -> int:
    keep_n = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    song_catalog = await fetch_song_catalog()
    known_titles = {title for title, _artist in song_catalog}

    lines = DATA_PATH.read_text(encoding="utf-8").splitlines()
    examples = [json.loads(line) for line in lines if line.strip()]

    clean = [e for e in examples if is_clean(e, known_titles)]
    dropped = len(examples) - len(clean)

    # 저장 전에 앞뒤 공백은 정리한다 (예: 선행 공백이 붙은 응답).
    for example in clean:
        for msg in example["messages"]:
            msg["content"] = msg["content"].strip()

    kept = clean[:keep_n]

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        for example in kept:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"원본 {len(examples)}개 중 깨진/환각 {dropped}개 제외, {len(kept)}개로 저장")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
