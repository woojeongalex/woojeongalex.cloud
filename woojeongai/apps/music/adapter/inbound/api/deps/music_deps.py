"""Music Use Case 조립 — DB 세션은 여기서만 주입."""

from music.dependencies.evaluation_director import get_evaluation_use_case
from music.dependencies.fletcher_director import get_fletcher_use_case
from music.dependencies.instrument_director import (
    get_instrument_catalog_use_case,
    get_instrument_recorder_use_case,
)
from music.dependencies.maestro_director import get_maestro_use_case
from music.dependencies.oracle_director import get_oracle_use_case
from music.dependencies.search_director import get_search_use_case
from music.dependencies.speech_director import (
    get_speech_recorder_use_case,
    get_speech_topic_use_case,
)
from music.dependencies.suggest_director import get_suggest_use_case
from music.dependencies.video_director import get_video_use_case

__all__ = [
    "get_evaluation_use_case",
    "get_fletcher_use_case",
    "get_instrument_catalog_use_case",
    "get_instrument_recorder_use_case",
    "get_maestro_use_case",
    "get_oracle_use_case",
    "get_search_use_case",
    "get_speech_recorder_use_case",
    "get_speech_topic_use_case",
    "get_suggest_use_case",
    "get_video_use_case",
]
