from __future__ import annotations

import logging

from neo4j import AsyncDriver

from star_craft.app.ports.output.graph_classification_port import (
    GraphClassificationPort,
)

logger = logging.getLogger(__name__)

_MERGE_QUERY = """
MERGE (n:ImageClassification {filename: $filename})
SET n.label = $label, n.confidence = $confidence, n.updated_at = timestamp()
RETURN elementId(n) AS node_id
"""


class Neo4jClassificationRepository(GraphClassificationPort):
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def save_classification(
        self, filename: str, label: str, confidence: float
    ) -> str:
        async with self._driver.session() as session:
            result = await session.run(
                _MERGE_QUERY, filename=filename, label=label, confidence=confidence
            )
            record = await result.single()

        node_id = str(record["node_id"]) if record else ""
        logger.info(
            f"[Neo4jClassificationRepository] 저장 완료 | filename={filename} "
            f"label={label} node_id={node_id}"
        )
        return node_id
