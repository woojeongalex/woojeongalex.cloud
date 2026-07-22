from __future__ import annotations

import asyncio

from star_craft.app.dtos.convnext_dto import ClassifyCommand, ClassifyResponse
from star_craft.app.ports.input.convnext_agent_use_case import ConvNextAgentUseCase
from star_craft.app.ports.output.classification_queue_port import (
    ClassificationQueuePort,
)
from star_craft.app.ports.output.graph_classification_port import (
    GraphClassificationPort,
)
from star_craft.app.tools.convnext_classify_tool import classify_image


class ConvNextAgentInteractor(ConvNextAgentUseCase):
    def __init__(self, graph: GraphClassificationPort, queue: ClassificationQueuePort):
        self.graph = graph
        self.queue = queue

    async def classify_and_store(self, cmd: ClassifyCommand) -> ClassifyResponse:
        result = await asyncio.to_thread(classify_image, cmd.image_bytes)

        node_id = await self.graph.save_classification(
            filename=cmd.filename,
            label=result.label,
            confidence=result.confidence,
        )
        queue_task_id = await self.queue.enqueue_post_process(
            node_id=node_id, label=result.label
        )

        return ClassifyResponse(
            node_id=node_id,
            label=result.label,
            confidence=result.confidence,
            queue_task_id=queue_task_id,
        )
