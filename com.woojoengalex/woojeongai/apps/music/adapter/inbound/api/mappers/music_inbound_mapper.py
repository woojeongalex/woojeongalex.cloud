"""Music inbound — HTTP 스키마 ↔ app/dtos 변환 (Adapter 경계 1회)."""
from __future__ import annotations

from music.adapter.inbound.api.schemas.instrument_andrew_recorder_schema import InstrumentEvaluationCreateRequest
from music.adapter.inbound.api.schemas.instrument_fletcher_tuner_schema import InstrumentEvaluationResponse
from music.adapter.inbound.api.schemas.instrument_franz_catalog_schema import (
    InstrumentCatalogHit,
    InstrumentCatalogResponse,
)
from music.adapter.inbound.api.schemas.speech_cicero_topic_schema import (
    SpeechTopicHit,
    SpeechTopicsResponse,
)
from music.adapter.inbound.api.schemas.speech_herald_recorder_schema import SpeechEvaluationCreateRequest
from music.adapter.inbound.api.schemas.speech_lumiere_video_schema import VideoVocalAnalysisResponse
from music.adapter.inbound.api.schemas.speech_oracle_analyst_schema import SpeechEvaluationResponse
from music.adapter.inbound.api.schemas.vocal_bard_searcher_schema import SongMrHitResponse, SongMrSearchResponse
from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import VocalEvaluationResponse
from music.adapter.inbound.api.schemas.vocal_mia_recorder_schema import VocalEvaluationCreateRequest
from music.adapter.inbound.api.schemas.vocal_muse_recommender_schema import (
    VocalRecommendationCreateRequest,
    VocalRecommendationResponse,
)
from music.app.dtos.evaluation_dto import (
    VocalEvaluationCreateCommand,
    VocalEvaluationResultDto,
)
from music.app.dtos.instrument_dto import (
    InstrumentCatalogHitDto,
    InstrumentCatalogResultDto,
    InstrumentEvaluationCreateCommand,
    InstrumentEvaluationResultDto,
)
from music.app.dtos.search_dto import SongMrHitDto, SongMrSearchResultDto
from music.app.dtos.speech_dto import (
    SpeechEvaluationCreateCommand,
    SpeechEvaluationResultDto,
    SpeechTopicHitDto,
    SpeechTopicsResultDto,
)
from music.app.dtos.suggest_dto import (
    VocalRecommendationCreateCommand,
    VocalRecommendationResultDto,
)
from music.app.dtos.video_analysis_dto import VideoVocalAnalysisResultDto


def to_search_response(dto: SongMrSearchResultDto) -> SongMrSearchResponse:
    return SongMrSearchResponse(
        query=dto.query,
        hits=[
            SongMrHitResponse(
                id=h.id,
                catalog_song_id=h.catalog_song_id,
                title=h.title,
                artist=h.artist,
                bpm=h.bpm,
                song_key=h.song_key,
                range_label=h.range_label,
                mr_track_name=h.mr_track_name,
                mr_description=h.mr_description,
            )
            for h in dto.hits
        ],
        count=dto.count,
    )


def from_evaluation_create(body: VocalEvaluationCreateRequest) -> VocalEvaluationCreateCommand:
    return VocalEvaluationCreateCommand(
        pitch_score=body.pitch_score,
        rhythm_score=body.rhythm_score,
        vocal_grade=body.vocal_grade,
        summary=body.summary,
        catalog_song_id=body.catalog_song_id,
        mr_search_list_id=body.mr_search_list_id,
        input_source=body.input_source,
        file_name=body.file_name,
        duration_sec=body.duration_sec,
    )


def to_evaluation_response(dto: VocalEvaluationResultDto) -> VocalEvaluationResponse:
    return VocalEvaluationResponse(id=dto.id, ok=dto.ok, message=dto.message)


def from_suggest_create(body: VocalRecommendationCreateRequest) -> VocalRecommendationCreateCommand:
    return VocalRecommendationCreateCommand(sing_evaluation_id=body.sing_evaluation_id)


def to_suggest_response(dto: VocalRecommendationResultDto) -> VocalRecommendationResponse:
    return VocalRecommendationResponse(
        id=dto.id,
        sing_evaluation_id=dto.sing_evaluation_id,
        pitch_score_snapshot=dto.pitch_score_snapshot,
        rhythm_score_snapshot=dto.rhythm_score_snapshot,
        vocal_grade_snapshot=dto.vocal_grade_snapshot,
        vocalization_pattern=dto.vocalization_pattern,
        recommended_genres=dto.recommended_genres,
        recommended_songs=dto.recommended_songs,
    )


def to_instrument_catalog_response(dto: InstrumentCatalogResultDto) -> InstrumentCatalogResponse:
    return InstrumentCatalogResponse(
        query=dto.query,
        hits=[
            InstrumentCatalogHit(
                instrument_id=h.instrument_id,
                label=h.label,
                description=h.description,
                standard_tuning=h.standard_tuning,
            )
            for h in dto.hits
        ],
        count=dto.count,
    )


def from_instrument_create(
    body: InstrumentEvaluationCreateRequest,
) -> InstrumentEvaluationCreateCommand:
    return InstrumentEvaluationCreateCommand(
        instrument_id=body.instrument_id,
        tuning_accuracy=body.tuning_accuracy,
        pitch_deviation_cents=body.pitch_deviation_cents,
        summary=body.summary,
        string_readings=body.string_readings,
        file_name=body.file_name,
        duration_sec=body.duration_sec,
    )


def to_instrument_response(dto: InstrumentEvaluationResultDto) -> InstrumentEvaluationResponse:
    return InstrumentEvaluationResponse(id=dto.id, ok=dto.ok, message=dto.message)


def to_speech_topics_response(dto: SpeechTopicsResultDto) -> SpeechTopicsResponse:
    return SpeechTopicsResponse(
        hits=[
            SpeechTopicHit(
                topic_id=h.topic_id,
                label=h.label,
                description=h.description,
            )
            for h in dto.hits
        ],
        count=dto.count,
    )


def from_speech_create(body: SpeechEvaluationCreateRequest) -> SpeechEvaluationCreateCommand:
    return SpeechEvaluationCreateCommand(
        topic_id=body.topic_id,
        clarity_score=body.clarity_score,
        pace_score=body.pace_score,
        tone_score=body.tone_score,
        summary=body.summary,
        feedback_points=body.feedback_points,
        file_name=body.file_name,
        duration_sec=body.duration_sec,
    )


def to_speech_response(dto: SpeechEvaluationResultDto) -> SpeechEvaluationResponse:
    return SpeechEvaluationResponse(id=dto.id, ok=dto.ok, message=dto.message)


def to_video_analysis_response(dto: VideoVocalAnalysisResultDto) -> VideoVocalAnalysisResponse:
    return VideoVocalAnalysisResponse(
        pitch_data=dto.pitch_data,
        bpm=dto.bpm,
        duration=dto.duration,
        emotions=dto.emotions,
    )
