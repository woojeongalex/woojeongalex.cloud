from __future__ import annotations

import asyncio

from core.matrix.local_llm_client import get_local_llm_client
from star_craft.app.ports.input.graph_qa_use_case import GraphQaUseCase
from star_craft.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from star_craft.app.ports.input.semantic_router_use_case import SemanticRouterUseCase
from star_craft.app.ports.output.gemini_chat_port import GeminiChatPort
from star_craft.domain.constants.semantic_intent_examples import (
    CODING_INTENT_EXAMPLES,
    GENERAL_INTENT_EXAMPLES,
    GRAPH_INTENT_EXAMPLES,
)
from star_craft.domain.services.semantic_intent_classifier import (
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
            "graph": [client.embed(text) for text in GRAPH_INTENT_EXAMPLES],
            "general": [client.embed(text) for text in GENERAL_INTENT_EXAMPLES],
            "coding": [client.embed(text) for text in CODING_INTENT_EXAMPLES],
        }
    return _example_vectors_cache


class SemanticRouterInteractor(SemanticRouterUseCase):
    def __init__(
        self,
        graph_qa: GraphQaUseCase,
        gemini: GeminiChatPort,
        langchain_chat: LangchainChatUseCase,
    ):
        self.graph_qa = graph_qa
        self.gemini = gemini
        self.langchain_chat = langchain_chat

    async def route(self, message: str) -> str:
        client = get_local_llm_client()
        query_vector = await asyncio.to_thread(client.embed, message)
        examples = await asyncio.to_thread(_embed_examples)
        intent = classify_intent(
            query_vector, examples["graph"], examples["general"], examples["coding"]
        )

        if intent is SemanticIntent.GRAPH:
            return await self.graph_qa.answer(message)
        if intent is SemanticIntent.CODING:
            return await self.langchain_chat.chat(message)
        return await asyncio.to_thread(self.gemini.generate, message)
