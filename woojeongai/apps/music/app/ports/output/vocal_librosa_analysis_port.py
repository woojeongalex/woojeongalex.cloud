"""[Layer: Ports] librosa 분석 outbound 포트 — 리소스 어댑터 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.outbound.librosa.librosa_vocal_analyzer import LibrosaAnalysisResult


class VocalLibrosaPort(ABC):
    @abstractmethod
    def analyze(self, audio_bytes: bytes, content_type: str) -> LibrosaAnalysisResult:
        """CPU-bound 동기 분석. 호출 측: asyncio.to_thread."""
