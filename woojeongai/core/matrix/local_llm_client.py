"""로컬 GPU 호스트(ship 데스크탑)에서 돌아가는 vLLM(EXAONE 등)을 호출하는 클라이언트.

`core/matrix/secret_manager.py`의 Gemini 클라이언트(Keymaker)와 나란히 두는
로컬 LLM 어댑터. vLLM의 OpenAI 호환 서버(`vllm serve ...`)를 HTTP로 호출한다.
"""

from __future__ import annotations

import os
from typing import Any

import requests

_DEFAULT_MODEL = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct-AWQ"


class LocalLLMClient:
    _instance: LocalLLMClient | None = None

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self._base_url = (
            base_url if base_url is not None else os.getenv("LOCAL_LLM_BASE_URL") or ""
        ).rstrip("/")
        self._model = model or os.getenv("LOCAL_LLM_MODEL") or _DEFAULT_MODEL

    @classmethod
    def instance(cls) -> LocalLLMClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def is_ready(self) -> bool:
        return bool(self._base_url)

    def generate(
        self, message: str, system_prompt: str | None = None, timeout: float = 120.0
    ) -> str:
        if not self.is_ready():
            raise RuntimeError(
                "LOCAL_LLM_BASE_URL이 설정되지 않았습니다. backend/.env를 확인하세요."
            )

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload: dict[str, Any] = {"model": self._model, "messages": messages}
        response = requests.post(
            f"{self._base_url}/v1/chat/completions", json=payload, timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


def get_local_llm_client() -> LocalLLMClient:
    return LocalLLMClient.instance()
