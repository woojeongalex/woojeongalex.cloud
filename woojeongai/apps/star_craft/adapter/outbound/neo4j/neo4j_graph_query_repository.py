from __future__ import annotations

from typing import Any

from neo4j import AsyncGraphDatabase

from star_craft.app.ports.output.graph_query_port import GraphQueryPort

_RECENT_QUERY = """
MATCH (n:ImageClassification)
RETURN n.filename AS filename, n.label AS label, n.confidence AS confidence
ORDER BY n.updated_at DESC
LIMIT $limit
"""


class Neo4jGraphQueryRepository(GraphQueryPort):
    """드라이버는 실제 조회 시점에만 연다 — 다른 의도(general/coding)로 분류된
    요청까지 Neo4j 설정 누락 때문에 실패하지 않도록 생성자에서는 연결하지 않는다."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._uri = uri
        self._auth = (user, password)

    async def find_recent_classifications(self, limit: int) -> list[dict[str, Any]]:
        if not self._uri:
            raise RuntimeError(
                "NEO4J_URI가 설정되지 않았습니다. backend/.env를 확인하세요."
            )
        driver = AsyncGraphDatabase.driver(self._uri, auth=self._auth)
        try:
            async with driver.session() as session:
                result = await session.run(_RECENT_QUERY, limit=limit)
                records = [record.data() async for record in result]
        finally:
            await driver.close()
        return records
