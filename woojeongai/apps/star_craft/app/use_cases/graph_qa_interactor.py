from __future__ import annotations

import asyncio
from typing import Any

from star_craft.app.ports.input.graph_qa_use_case import GraphQaUseCase
from star_craft.app.ports.output.gemini_chat_port import GeminiChatPort
from star_craft.app.ports.output.graph_query_port import GraphQueryPort

_RECENT_LIMIT = 10


def _format_context(records: list[dict[str, Any]]) -> str:
    if not records:
        return "그래프 DB에 저장된 분류 데이터가 아직 없습니다."
    lines = [
        f"- {r.get('filename')}: {r.get('label')} (신뢰도 {r.get('confidence')})"
        for r in records
    ]
    return "최근 저장된 분류 데이터:\n" + "\n".join(lines)


class GraphQaInteractor(GraphQaUseCase):
    def __init__(self, graph_query: GraphQueryPort, gemini: GeminiChatPort):
        self.graph_query = graph_query
        self.gemini = gemini

    async def answer(self, message: str) -> str:
        records = await self.graph_query.find_recent_classifications(_RECENT_LIMIT)
        context = _format_context(records)
        prompt = f"{context}\n\n위 데이터를 참고해서 다음 질문에 한국어로 답하세요: {message}"
        return await asyncio.to_thread(self.gemini.generate, prompt)
