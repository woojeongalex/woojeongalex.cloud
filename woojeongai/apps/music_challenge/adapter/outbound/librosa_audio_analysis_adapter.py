"""[Layer: Adapter Outbound] AudioAnalysisPort 구현체 — librosa 기반.

music 앱의 analyze_vocal_sync 를 재사용한다. 상태가 없는 순수 함수라
앱 간 결합이라기보다 공용 유틸에 가깝다.

TODO: 오디오 분석은 특정 앱의 것이 아니라 공용 인프라이므로 언젠가
core/ 로 옮기는 편이 맞다. 지금 옮기면 동작 중인 music 앱을 건드려야 해서
미뤄둔다.
"""

import logging

from music.adapter.outbound.librosa.librosa_vocal_analyzer import analyze_vocal_sync
from music_challenge.app.ports.output.audio_analysis_port import (
    AudioAnalysisPort,
    AudioMetrics,
)

logger = logging.getLogger(__name__)


class LibrosaAudioAnalysisAdapter(AudioAnalysisPort):
    def analyze(self, audio_bytes: bytes, content_type: str) -> AudioMetrics | None:
        try:
            result = analyze_vocal_sync(audio_bytes, content_type)
        except Exception as e:
            logger.warning("librosa 분석 실패 (%s): %s", content_type, e)
            return None

        return AudioMetrics(
            pitch_score=result.pitch_score,
            rhythm_score=result.rhythm_score,
            tempo=result.tempo,
            mean_hz=result.mean_hz,
            std_hz=result.std_hz,
            duration=result.duration,
        )
