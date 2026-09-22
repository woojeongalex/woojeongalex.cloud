from abc import ABC, abstractmethod

from music_challenge.domain.value_objects.rhythm_vo import RhythmAnalysis


class RhythmAnalyzerPort(ABC):
    @abstractmethod
    def analyze(self, audio: bytes) -> RhythmAnalysis:
        """완성곡에서 박자와 소리 시작 순간을 찾는다. CPU 작업이라 동기 함수다."""
