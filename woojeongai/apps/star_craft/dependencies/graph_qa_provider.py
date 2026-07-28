import os

from fastapi import Depends

from star_craft.adapter.outbound.neo4j.neo4j_graph_query_repository import (
    Neo4jGraphQueryRepository,
)
from star_craft.app.ports.input.graph_qa_use_case import GraphQaUseCase
from star_craft.app.ports.output.gemini_chat_port import GeminiChatPort
from star_craft.app.ports.output.graph_query_port import GraphQueryPort
from star_craft.app.use_cases.graph_qa_interactor import GraphQaInteractor
from star_craft.dependencies.gemini_chat_provider import get_gemini_chat_gateway

_NEO4J_URI = os.getenv("NEO4J_URI", "")
_NEO4J_USER = os.getenv("NEO4J_USER", "")
_NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")


def get_graph_query_repository() -> GraphQueryPort:
    return Neo4jGraphQueryRepository(
        uri=_NEO4J_URI, user=_NEO4J_USER, password=_NEO4J_PASSWORD
    )


def get_graph_qa_use_case(
    graph_query: GraphQueryPort = Depends(get_graph_query_repository),
    gemini: GeminiChatPort = Depends(get_gemini_chat_gateway),
) -> GraphQaUseCase:
    return GraphQaInteractor(graph_query=graph_query, gemini=gemini)
