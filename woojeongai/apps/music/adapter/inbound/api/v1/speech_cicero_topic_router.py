from fastapi import APIRouter, Depends

from music.adapter.inbound.api.mappers.music_inbound_mapper import to_speech_topics_response
from music.adapter.inbound.api.schemas.speech_cicero_topic_schema import CiceroIntroduceSchema, CiceroIntroduceResponse, SpeechTopicsResponse
from music.app.ports.input.speech_cicero_topic_use_case import SpeechTopicUseCase
from music.adapter.inbound.api.deps.music_deps import get_speech_topic_use_case

speech_cicero_topic_router = APIRouter(tags=["music-speech"])


@speech_cicero_topic_router.get("/api/music/cicero/myself", response_model=CiceroIntroduceResponse)
async def cicero_introduce_myself(
    cicero: SpeechTopicUseCase = Depends(get_speech_topic_use_case),
) -> CiceroIntroduceResponse:
    return await cicero.introduce_myself(CiceroIntroduceSchema(id=7, name="스피치 키케로 (Cicero)"))


@speech_cicero_topic_router.get("/api/music/speech-topics", response_model=SpeechTopicsResponse)
async def get_speech_topics(
    speech: SpeechTopicUseCase = Depends(get_speech_topic_use_case),
) -> SpeechTopicsResponse:
    return to_speech_topics_response(speech.read_topics())
