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


# 음악으로 잘못 분류하면 헨드릭스 페르소나가 사실을 지어내 답하는 반면, 일반으로
# 잘못 분류해도 Gemini가 무난하게 답할 뿐이라 실패 비용이 비대칭적이다. 그래서
# 애매한 경우(근소한 차이)는 GENERAL 쪽으로 기울인다 -- MUSIC이라 판단하려면
# 일정 마진 이상 확실히 앞서야 한다.
_MUSIC_CONFIDENCE_MARGIN = 0.03


def classify_intent(
    query_vector: list[float],
    music_vectors: list[list[float]],
    general_vectors: list[list[float]],
) -> SemanticIntent:
    music_score = max(
        (cosine_similarity(query_vector, v) for v in music_vectors), default=0.0
    )
    general_score = max(
        (cosine_similarity(query_vector, v) for v in general_vectors), default=0.0
    )
    if music_score - general_score > _MUSIC_CONFIDENCE_MARGIN:
        return SemanticIntent.MUSIC
    return SemanticIntent.GENERAL
