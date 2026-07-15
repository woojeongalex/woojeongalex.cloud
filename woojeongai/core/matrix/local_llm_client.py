"""로컬 GPU 호스트에서 돌아가는 vLLM(EXAONE 등)을 호출하는 클라이언트.

`core/matrix/secret_manager.py`의 Gemini 클라이언트(Keymaker)와 나란히 두는
로컬 LLM 어댑터. vLLM의 OpenAI 호환 서버(`vllm serve ...`)를 HTTP로 호출한다.

생성(chat)과 임베딩(embed)은 서로 다른 vLLM 인스턴스(각각 `--runner generate`,
`--runner pooling --convert embed`)로 항상 함께 떠 있는 것을 전제로 한다 —
VRAM이 넉넉한 호스트에서는 같은 모델을 두 개의 독립된 엔드포인트로 동시에
서빙하면 되고, 이 클라이언트는 그 두 엔드포인트를 호출하기만 한다. 한 GPU에
하나만 띄울 수 있는 개발 환경(예: 8GB급 데스크탑)에서는
`apps/silicon_valley/ops/vllm_mode_controller.py`로 수동으로 모드를 바꿔가며
테스트한다 — 그건 로컬 개발용 보조 도구일 뿐, 이 클라이언트나 요청 처리
경로에는 관여하지 않는다.
"""

from __future__ import annotations

import os
from typing import Any

import requests

_DEFAULT_MODEL = (
    "EXAONE-3.5-7.8B-Instruct-AWQ"  # vllm serve --served-model-name과 일치해야 함
)


class LocalLLMClient:
    _instance: LocalLLMClient | None = None

    def __init__(
        self,
        base_url: str | None = None,
        embed_base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._base_url = (
            base_url if base_url is not None else os.getenv("LOCAL_LLM_BASE_URL") or ""
        ).rstrip("/")
        self._embed_base_url = (
            embed_base_url
            if embed_base_url is not None
            else os.getenv("LOCAL_LLM_EMBED_BASE_URL") or ""
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

    def is_embed_ready(self) -> bool:
        return bool(self._embed_base_url)

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

    def embed(self, text_input: str, timeout: float = 120.0) -> list[float]:
        if not self.is_embed_ready():
            raise RuntimeError(
                "LOCAL_LLM_EMBED_BASE_URL이 설정되지 않았습니다. backend/.env를 확인하세요."
            )

        payload: dict[str, Any] = {"model": self._model, "input": text_input}
        response = requests.post(
            f"{self._embed_base_url}/v1/embeddings", json=payload, timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


def get_local_llm_client() -> LocalLLMClient:
    return LocalLLMClient.instance()
