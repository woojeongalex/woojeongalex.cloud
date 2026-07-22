"""[Layer: Adapter Outbound] VocalLibrosaPort 구현체."""
from __future__ import annotations

from music.adapter.outbound.librosa.librosa_vocal_analyzer import (
    LibrosaAnalysisResult,
    analyze_vocal_sync,
)
from music.app.ports.output.vocal_librosa_analysis_port import VocalLibrosaPort


class LibrosaVocalAdapter(VocalLibrosaPort):
    def analyze(self, audio_bytes: bytes, content_type: str = "audio/wav") -> LibrosaAnalysisResult:
        return analyze_vocal_sync(audio_bytes, content_type)
