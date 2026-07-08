"""선택적 공통 `.env` 선로드. API 키·클라이언트는 `matrix.app.keymaker.get_keymaker()`가 관리합니다."""

from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / ".env")
