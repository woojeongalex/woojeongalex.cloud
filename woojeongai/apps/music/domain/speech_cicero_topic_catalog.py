"""[Layer: Domain] Cicero 스피치 코칭 주제 (인메모리 · DB 미저장)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpeechTopicItem:
    topic_id: str
    label: str
    description: str


SPEECH_TOPICS: tuple[SpeechTopicItem, ...] = (
    SpeechTopicItem(
        topic_id="presentation",
        label="발표·프레젠테이션",
        description="발표 속도, 호흡, 강조 포인트",
    ),
    SpeechTopicItem(
        topic_id="interview",
        label="면접·자기소개",
        description="명확한 발음, 자신감 있는 톤",
    ),
    SpeechTopicItem(
        topic_id="daily",
        label="일상 대화",
        description="자연스러운 말하기, 끊김 줄이기",
    ),
    SpeechTopicItem(
        topic_id="pronunciation",
        label="발음·억양",
        description="또박또박한 발음과 억양 연습",
    ),
)


def list_speech_topics() -> list[SpeechTopicItem]:
    return list(SPEECH_TOPICS)


def get_speech_topic(topic_id: str) -> SpeechTopicItem | None:
    key = topic_id.strip().lower()
    for item in SPEECH_TOPICS:
        if item.topic_id == key:
            return item
    return None
