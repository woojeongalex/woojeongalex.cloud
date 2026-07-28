from fastapi import Depends

from star_craft.app.ports.input.graph_qa_use_case import GraphQaUseCase
from star_craft.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from star_craft.app.ports.input.semantic_router_use_case import SemanticRouterUseCase
from star_craft.app.ports.output.gemini_chat_port import GeminiChatPort
from star_craft.app.use_cases.semantic_router_interactor import (
    SemanticRouterInteractor,
)
from star_craft.dependencies.gemini_chat_provider import get_gemini_chat_gateway
from star_craft.dependencies.graph_qa_provider import get_graph_qa_use_case
from star_craft.dependencies.langchain_chat_provider import get_langchain_chat_use_case


def get_semantic_router_use_case(
    graph_qa: GraphQaUseCase = Depends(get_graph_qa_use_case),
    gemini: GeminiChatPort = Depends(get_gemini_chat_gateway),
    langchain_chat: LangchainChatUseCase = Depends(get_langchain_chat_use_case),
) -> SemanticRouterUseCase:
    return SemanticRouterInteractor(
        graph_qa=graph_qa, gemini=gemini, langchain_chat=langchain_chat
    )
