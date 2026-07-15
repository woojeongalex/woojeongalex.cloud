from __future__ import annotations

import asyncio

from core.matrix.local_llm_client import get_local_llm_client
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import (
    HendricksCeoUseCase,
)
from silicon_valley.app.ports.input.semantic_router_use_case import (
    SemanticRouterUseCase,
)
from silicon_valley.app.ports.output.gemini_port import GeminiPort
from silicon_valley.domain.constants.semantic_intent_examples import (
    GENERAL_INTENT_EXAMPLES,
    MUSIC_INTENT_EXAMPLES,
)
from silicon_valley.domain.services.semantic_intent_classifier import (
    SemanticIntent,
    classify_intent,
)

_example_vectors_cache: dict[str, list[list[float]]] | None = None


def _embed_examples() -> dict[str, list[list[float]]]:
    """의도 분류 기준 문장들의 임베딩. 고정된 문장이라 프로세스당 한 번만 계산해 캐싱한다."""
    global _example_vectors_cache
    if _example_vectors_cache is None:
        client = get_local_llm_client()
        _example_vectors_cache = {
            "music": [client.embed(text) for text in MUSIC_INTENT_EXAMPLES],
            "general": [client.embed(text) for text in GENERAL_INTENT_EXAMPLES],
        }
    return _example_vectors_cache


class SemanticRouterInteractor(SemanticRouterUseCase):
    def __init__(self, hendricks: HendricksCeoUseCase, gemini: GeminiPort):
        self.hendricks = hendricks
        self.gemini = gemini

    async def route(self, message: str) -> str:
        client = get_local_llm_client()
        query_vector = await asyncio.to_thread(client.embed, message)
        examples = await asyncio.to_thread(_embed_examples)
        intent = classify_intent(query_vector, examples["music"], examples["general"])

        if intent is SemanticIntent.MUSIC:
            return await self.hendricks.chat(message)
        return await asyncio.to_thread(self.gemini.generate, message)
