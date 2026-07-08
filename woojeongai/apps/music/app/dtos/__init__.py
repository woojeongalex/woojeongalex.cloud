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

__all__ = [
    "SongMrHitDto",
    "SongMrSearchResultDto",
    "VocalEvaluationCreateCommand",
    "VocalEvaluationResultDto",
    "VocalRecommendationCreateCommand",
    "VocalRecommendationResultDto",
    "InstrumentCatalogHitDto",
    "InstrumentCatalogResultDto",
    "InstrumentEvaluationCreateCommand",
    "InstrumentEvaluationResultDto",
    "SpeechTopicHitDto",
    "SpeechTopicsResultDto",
    "SpeechEvaluationCreateCommand",
    "SpeechEvaluationResultDto",
    "VideoVocalAnalysisResultDto",
]
