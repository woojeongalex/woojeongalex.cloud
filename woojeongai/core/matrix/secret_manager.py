"""시스템 전역 환경 변수·비밀 값을 한곳에서 읽습니다.

예전에는 여기서 Gemini 클라이언트도 만들어 뒀다. `.env` 를 한 번이라도 읽으면
그때 `google.generativeai` 가 같이 import 되는 구조였다 — AWS 자격 하나를 꺼낼
때도 그랬다. Gemini 를 걷어내면서 이 파일은 환경 변수 읽기만 남겼다.
"""

from __future__ import annotations

import os
from pathlib import Path


def default_backend_env_path() -> Path:
    """`backend/.env` 경로 (`core/matrix/keymaker_api.py` 기준)."""
    return Path(__file__).resolve().parents[2] / ".env"


class Keymaker:
    """
    전역 키·설정 관리자.

    - `backend/.env` 를 한 번만 로드
    - 이름으로 비밀 값 조회 (`get_secret`)
    """

    _instance: Keymaker | None = None

    def __init__(self, env_path: Path | None = None) -> None:
        self._env_path = env_path or default_backend_env_path()
        self._dotenv_loaded = False

    @classmethod
    def instance(cls, env_path: Path | None = None) -> Keymaker:
        """프로세스당 하나의 Keymaker (첫 생성 시 env_path만 적용)."""
        if cls._instance is None:
            cls._instance = cls(env_path=env_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """테스트 등에서 인스턴스를 비울 때만 사용."""
        cls._instance = None

    def load_env(self) -> None:
        """`.env`를 한 번만 로드하고, 등록된 클라이언트를 부트스트랩합니다."""
        if self._dotenv_loaded:
            return
        from dotenv import load_dotenv

        load_dotenv(self._env_path)
        self._dotenv_loaded = True

    def get_secret(self, name: str, default: str = "") -> str:
        """임의 환경 변수(민감 값) 조회. 필요 시 `.env` 로드를 트리거합니다."""
        self.load_env()
        return (os.getenv(name) or default).strip()


def get_keymaker(env_path: Path | None = None) -> Keymaker:
    """애플리케이션 전역에서 사용할 Keymaker 싱글톤."""
    return Keymaker.instance(env_path=env_path)
