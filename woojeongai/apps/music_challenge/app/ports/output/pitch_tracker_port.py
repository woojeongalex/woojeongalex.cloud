from abc import ABC, abstractmethod

from music_challenge.domain.value_objects.chart_vo import MelodySource


class PitchTrackerPort(ABC):
    """제출된 녹음의 음높이를 시간순으로 잰다. CPU-bound 동기 함수다."""

    @abstractmethod
    def track(
        self, audio_bytes: bytes, source: MelodySource
    ) -> list[tuple[float, float | None]]:
        """(녹음 시작 기준 초, MIDI 음높이 또는 None) 목록. 음이 아니면 None."""
