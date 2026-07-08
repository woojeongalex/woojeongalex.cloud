from music.adapter.inbound.api.v1.instrument_andrew_recorder_router import instrument_andrew_recorder_router
from music.adapter.inbound.api.v1.instrument_franz_catalog_router import instrument_franz_catalog_router
from music.adapter.inbound.api.v1.speech_cicero_topic_router import speech_cicero_topic_router
from music.adapter.inbound.api.v1.speech_herald_recorder_router import speech_herald_recorder_router
from music.adapter.inbound.api.v1.speech_lumiere_video_router import speech_lumiere_video_router
from music.adapter.inbound.api.v1.vocal_bard_searcher_router import vocal_bard_searcher_router
from music.adapter.inbound.api.v1.vocal_mia_recorder_router import vocal_mia_recorder_router
from music.adapter.inbound.api.v1.vocal_muse_recommender_router import vocal_muse_recommender_router

__all__ = [
    "vocal_bard_searcher_router",
    "vocal_mia_recorder_router",
    "vocal_muse_recommender_router",
    "instrument_franz_catalog_router",
    "instrument_andrew_recorder_router",
    "speech_cicero_topic_router",
    "speech_herald_recorder_router",
    "speech_lumiere_video_router",
]
