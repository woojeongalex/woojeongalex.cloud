"""Video(Lumière) 의존성 조립소 — 영상 업로드 분석 (DB 없음)."""

from music.app.ports.input.speech_lumiere_video_use_case import VideoAnalysisUseCase
from music.app.use_cases.speech_lumiere_video_interactor import LumiereVideoInteractor


def get_video_use_case() -> VideoAnalysisUseCase:
    return LumiereVideoInteractor()
