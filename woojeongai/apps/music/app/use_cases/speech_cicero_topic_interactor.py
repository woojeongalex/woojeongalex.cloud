from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.speech_cicero_topic_schema import CiceroIntroduceSchema, CiceroIntroduceResponse
from music.app.dtos.speech_dto import CiceroIntroduceQuery, SpeechTopicHitDto, SpeechTopicsResultDto
from music.app.ports.input.speech_cicero_topic_use_case import SpeechTopicUseCase
from music.app.ports.output.speech_herald_recorder_port import SpeechPort
from music.domain.speech_cicero_topic_catalog import list_speech_topics

logger = logging.getLogger(__name__)


class CiceroTopicInteractor(SpeechTopicUseCase):
    def __init__(self, repository: SpeechPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: CiceroIntroduceSchema) -> CiceroIntroduceResponse:
        return await self.repository.introduce_cicero(CiceroIntroduceQuery(id=schema.id, name=schema.name))

    def read_topics(self) -> SpeechTopicsResultDto:
        hits = [
            SpeechTopicHitDto(
                topic_id=item.topic_id,
                label=item.label,
                description=item.description,
            )
            for item in list_speech_topics()
        ]
        logger.info("[MUSIC][cicero][4/interactor] 주제 조회 count=%d", len(hits))
        return SpeechTopicsResultDto(hits=hits, count=len(hits))
