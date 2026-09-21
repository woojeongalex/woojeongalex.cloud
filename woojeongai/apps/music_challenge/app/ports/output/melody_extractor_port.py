from abc import ABC, abstractmethod
from dataclasses import dataclass

from music_challenge.domain.value_objects.chart_vo import Note


@dataclass(frozen=True)
class ExtractedMelody:
    notes: list[Note]
    duration: float


class MelodyExtractorPort(ABC):
    """보컬 트랙에서 정답 멜로디를 뽑는다. CPU-bound 동기 함수다."""

    @abstractmethod
    def extract(self, audio_bytes: bytes) -> ExtractedMelody: ...
