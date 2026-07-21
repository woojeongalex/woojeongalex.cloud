from __future__ import annotations

import asyncio
import json
import logging
import time

from core.matrix.redis_client import RedisClient
from star_craft.app.ports.output.classification_queue_port import (
    ClassificationQueuePort,
)

logger = logging.getLogger(__name__)

REDIS_KEY = "star_craft:convnext:post_process"


class RedisClassificationQueue(ClassificationQueuePort):
    def __init__(self, client: RedisClient) -> None:
        self._client = client

    async def enqueue_post_process(self, node_id: str, label: str) -> str:
        enqueued_at = time.time()
        payload = json.dumps(
            {"node_id": node_id, "label": label, "enqueued_at": enqueued_at}
        )
        await asyncio.to_thread(self._client.rpush, REDIS_KEY, payload)

        task_id = f"task:{node_id}:{int(enqueued_at)}"
        logger.info(
            f"[RedisClassificationQueue] 적재 완료 | node_id={node_id} "
            f"label={label} task_id={task_id}"
        )
        return task_id
