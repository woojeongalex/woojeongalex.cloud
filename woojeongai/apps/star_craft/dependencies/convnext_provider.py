from __future__ import annotations

import os

from fastapi import Depends
from neo4j import AsyncGraphDatabase

from core.matrix.redis_client import RedisClient
from star_craft.adapter.outbound.neo4j.neo4j_classification_repository import (
    Neo4jClassificationRepository,
)
from star_craft.adapter.outbound.redis.redis_classification_queue import (
    RedisClassificationQueue,
)
from star_craft.app.ports.input.convnext_agent_use_case import ConvNextAgentUseCase
from star_craft.app.ports.output.classification_queue_port import (
    ClassificationQueuePort,
)
from star_craft.app.ports.output.graph_classification_port import (
    GraphClassificationPort,
)
from star_craft.app.use_cases.image_classifier_interactor import ConvNextAgentInteractor

_NEO4J_URI = os.getenv("NEO4J_URI", "")
_NEO4J_USER = os.getenv("NEO4J_USER", "")
_NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")


def get_graph_repository() -> GraphClassificationPort:
    driver = AsyncGraphDatabase.driver(_NEO4J_URI, auth=(_NEO4J_USER, _NEO4J_PASSWORD))
    return Neo4jClassificationRepository(driver=driver)


def get_queue_repository() -> ClassificationQueuePort:
    return RedisClassificationQueue(client=RedisClient())


def get_convnext_use_case(
    graph: GraphClassificationPort = Depends(get_graph_repository),
    queue: ClassificationQueuePort = Depends(get_queue_repository),
) -> ConvNextAgentUseCase:
    return ConvNextAgentInteractor(graph=graph, queue=queue)
