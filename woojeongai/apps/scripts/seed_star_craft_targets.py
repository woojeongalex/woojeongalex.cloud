# ruff: noqa: E402
"""크롤러·스크래퍼 테스트용으로 Redis에 대상(웹사이트+키워드)을 등록한다.

python3 seed_star_craft_targets.py <website> <keyword>
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

from core.matrix.redis_client import get_redis_client
from star_craft.adapter.outbound.redis.redis_crawl_target_repository import (
    REDIS_CRAWL_TARGETS_KEY,
)


def main() -> int:
    if len(sys.argv) != 3:
        print("사용법: python3 seed_star_craft_targets.py <website> <keyword>")
        return 1

    website, keyword = sys.argv[1], sys.argv[2]
    client = get_redis_client()
    client.rpush(REDIS_CRAWL_TARGETS_KEY, json.dumps({"website": website, "keyword": keyword}))
    print(f"등록 완료: {website} / {keyword}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
