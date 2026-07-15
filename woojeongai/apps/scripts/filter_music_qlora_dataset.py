# ruff: noqa: E402
"""music_mood_recommendations.jsonl에서 깨진 예시를 걸러내고 N개로 줄인다.

python3 filter_music_qlora_dataset.py [남길 개수(기본 30)]
"""

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


def is_clean(example: dict) -> bool:
    for msg in example["messages"]:
        content = msg["content"]
        if _GARBLED_PATTERN.search(content):
            return False
        if len(content.strip()) < 5:
            return False
    return True


def main() -> int:
    keep_n = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    lines = DATA_PATH.read_text(encoding="utf-8").splitlines()
    examples = [json.loads(line) for line in lines if line.strip()]

    clean = [e for e in examples if is_clean(e)]
    dropped = len(examples) - len(clean)
    kept = clean[:keep_n]

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        for example in kept:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"원본 {len(examples)}개 중 깨진 {dropped}개 제외, {len(kept)}개로 저장")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
