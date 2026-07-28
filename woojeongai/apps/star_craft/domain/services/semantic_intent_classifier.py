"""임베딩 벡터 간 코사인 유사도로 의도(그래프/일반/코딩)를 분류하는 순수 도메인 로직."""

from __future__ import annotations

import math
from enum import Enum


class SemanticIntent(str, Enum):
    GRAPH = "graph"
    GENERAL = "general"
    CODING = "coding"


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# GRAPH/CODING으로 잘못 분류하면 근거 없는 컨텍스트로 답하게 되는 반면, 일반으로
# 잘못 분류해도 Gemini가 무난하게 답할 뿐이라 실패 비용이 비대칭적이다. 그래서
# 애매한 경우(근소한 차이)는 GENERAL 쪽으로 기울인다 -- GRAPH/CODING이라 판단하려면
# 일정 마진 이상 확실히 앞서야 한다.
_GRAPH_CONFIDENCE_MARGIN = 0.03
_CODING_CONFIDENCE_MARGIN = 0.03


def classify_intent(
    query_vector: list[float],
    graph_vectors: list[list[float]],
    general_vectors: list[list[float]],
    coding_vectors: list[list[float]],
) -> SemanticIntent:
    graph_score = max(
        (cosine_similarity(query_vector, v) for v in graph_vectors), default=0.0
    )
    general_score = max(
        (cosine_similarity(query_vector, v) for v in general_vectors), default=0.0
    )
    coding_score = max(
        (cosine_similarity(query_vector, v) for v in coding_vectors), default=0.0
    )

    if coding_score - max(graph_score, general_score) > _CODING_CONFIDENCE_MARGIN:
        return SemanticIntent.CODING
    if graph_score - general_score > _GRAPH_CONFIDENCE_MARGIN:
        return SemanticIntent.GRAPH
    return SemanticIntent.GENERAL
