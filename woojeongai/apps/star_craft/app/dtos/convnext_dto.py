from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassifyCommand:
    filename: str
    content_type: str
    image_bytes: bytes


@dataclass(frozen=True)
class ClassifyResponse:
    node_id: str
    label: str
    confidence: float
    queue_task_id: str
