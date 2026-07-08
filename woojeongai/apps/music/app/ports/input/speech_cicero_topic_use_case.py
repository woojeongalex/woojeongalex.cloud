"""[Layer: Ports] 스피치 주제 입력 Port — 주제 조회 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.speech_cicero_topic_schema import CiceroIntroduceSchema, CiceroIntroduceResponse
from music.app.dtos.speech_dto import SpeechTopicsResultDto


class SpeechTopicUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: CiceroIntroduceSchema) -> CiceroIntroduceResponse:
        pass

    @abstractmethod
    def read_topics(self) -> SpeechTopicsResultDto:
        pass
