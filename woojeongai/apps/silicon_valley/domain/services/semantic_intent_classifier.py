"""임베딩 벡터 간 코사인 유사도로 의도(음악/일반)를 분류하는 순수 도메인 로직."""

from __future__ import annotations

import math
from enum import Enum


class SemanticIntent(str, Enum):
    MUSIC = "music"
    GENERAL = "general"


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def classify_intent(
    query_vector: list[float],
    music_vectors: list[list[float]],
    general_vectors: list[list[float]],
) -> SemanticIntent:
    music_score = max((cosine_similarity(query_vector, v) for v in music_vectors), default=0.0)
    general_score = max(
        (cosine_similarity(query_vector, v) for v in general_vectors), default=0.0
    )
    return SemanticIntent.MUSIC if music_score >= general_score else SemanticIntent.GENERAL
