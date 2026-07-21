from __future__ import annotations

from pydantic import BaseModel


class ConvNextClassifyResponse(BaseModel):
    node_id: str
    label: str
    confidence: float
    queue_task_id: str
